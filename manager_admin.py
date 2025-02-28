from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from datetime import date, datetime

from auth import manager_required
from db import get_db

bp = Blueprint("manager_admin", __name__, url_prefix="/manager/admin")

def alltrainer():
    db = get_db()
    db.execute('SELECT CONCAT(Firstname, " ", Lastname) AS "Trainer Name", StaffID FROM Staff WHERE IsTrainer = 1')
    all_trainer = db.fetchall()
    return all_trainer

@bp.route("/paymentinfo", methods = ["GET", "POST"])
@manager_required # this function need login first
def paymentinfo():
    """Show all the specialized training and membership fee payments in past 30 days."""
    # fetch membership fee payments info 
    db = get_db()
    sql1 = '''
        SELECT 
            p.PaymentID,
            CONCAT("$",p.Value) as Cost,
            p.PaymentDate AS "Pay Date",
            p.MemberID AS "Payer's MemberID",
            m.Firstname,
            m.Lastname,
            mt.Term AS "Membership Type",
            "Membership fee" AS "Payment name"
        FROM Payment p
        JOIN Member m USING (MemberID)
        JOIN MembershipTerm mt ON m.MembershipTerm = mt.MembershipTermID
        WHERE p.ScheduleID IS NULL
			AND p.PaymentDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            AND p.PaymentDate <= NOW()
	    ORDER BY p.PaymentDate asc'''
    db.execute(sql1)
    membershipfee_list = db.fetchall()
    column1_names = [desc[0] for desc in db.description]
    
    # fetch specialized training fee payments info
    db = get_db()
    sql2 = '''
        SELECT 
            p.PaymentID,
            CONCAT("$",p.Value) as Cost,
            p.PaymentDate AS "Pay Date",
            p.MemberID AS "Payer's MemberID",
            m.Firstname,
            m.Lastname,
            sc.ScheduleID,
            t.TrainingName AS "Class Name"
        FROM Payment p
        JOIN Member m USING (MemberID)
        JOIN Schedule sc USING (ScheduleID)
        JOIN Training t USING (TrainingID)
        JOIN Price pr on pr.PriceID = sc.PriceID
        WHERE pr.IsMembershipterm = 0
            AND p.PaymentDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            AND p.PaymentDate <= NOW()
	 ORDER BY p.PaymentDate asc'''
    db.execute(sql2)
    spetraining_list = db.fetchall()
    column2_names = [desc[0] for desc in db.description]
    return render_template("/manager/paymentinfo.html", db_result1 = membershipfee_list, db_cols1 = column1_names, db_result2 = spetraining_list, db_cols2 = column2_names)

@bp.route("/paymentinfo/membershipfee", methods = ["GET", "POST"])
@manager_required # this function need login first
def membershipfee():
    # fetch membership fee payments info 
    db = get_db()
    sql1 = '''
        SELECT 
            p.PaymentID,
            CONCAT("$",p.Value) as Cost,
            p.PaymentDate AS "Pay Date",
            p.MemberID AS "Payer's MemberID",
            m.Firstname,
            m.Lastname,
            mt.Term AS "Membership Type",
            "Membership fee" AS "Payment name"
        FROM Payment p
        JOIN Member m USING (MemberID)
        JOIN MembershipTerm mt ON m.MembershipTerm = mt.MembershipTermID
        WHERE p.ScheduleID IS NULL
			AND p.PaymentDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            AND p.PaymentDate <= NOW()
	 ORDER BY p.PaymentDate asc'''
    db.execute(sql1)
    membershipfee_list = db.fetchall()
    column1_names = [desc[0] for desc in db.description]
    return render_template("/manager/membershipfee.html", db_result1 = membershipfee_list, db_cols1 = column1_names)

@bp.route("/paymentinfo/trainingfee", methods = ["GET", "POST"])
@manager_required # this function need login first
def trainingfee():
    # fetch specialized training fee payments info
    db = get_db()
    sql2 = '''
        SELECT 
            p.PaymentID,
            CONCAT("$",p.Value) as Cost,
            p.PaymentDate AS "Pay Date",
            p.MemberID AS "Payer's MemberID",
            m.Firstname,
            m.Lastname,
            sc.ScheduleID,
            t.TrainingName AS "Class Name"
        FROM Payment p
        JOIN Member m USING (MemberID)
        JOIN Schedule sc USING (ScheduleID)
        JOIN Training t USING (TrainingID)
        JOIN Price pr on pr.PriceID = sc.PriceID
        WHERE pr.IsMembershipterm = 0
            AND p.PaymentDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            AND p.PaymentDate <= NOW()
	ORDER BY p.PaymentDate asc'''
    db.execute(sql2)
    spetraining_list = db.fetchall()
    column2_names = [desc[0] for desc in db.description]
    return render_template("/manager/trainingfee.html", db_result2 = spetraining_list, db_cols2 = column2_names)

@bp.route("/class", methods = ["GET", "POST"])
@manager_required # this function need login first
def classtype():
    return render_template("/manager/classtype.html")

@bp.route("/class/", methods = ["POST"])
@manager_required # this function need login first
def selectclass():
    """Show group class or specialized training information if selected"""    
    if request.method == "POST":
        class_type = request.form.get('class_type')
        if class_type == "specialized training":
            return redirect(url_for("manager_admin.st"))
        
        else:
            all_trainer = alltrainer()
            select_trainerID = request.form.get('trainerID')
            if select_trainerID is not None:
                db = get_db()
                sql = '''
                    SELECT 
                        sc.StartDate AS "Date",
                        sc.StartTime AS "Start Time",
                        sc.EndTime AS "End Time",
                        t.TrainingName AS "Class Name",
                        CONCAT(st.Firstname, " ", st.Lastname) AS "Trainer Name",
                        COUNT(b.MemberID) AS "Booking Count",
                        IFNULL(SUM(b.IsAttended), 0) AS "Attendance Count"
                    FROM Schedule sc
                    JOIN Training t USING (TrainingID) 
                    JOIN Staff st USING (StaffID)
                    LEFT JOIN Booking b USING (ScheduleID)
                    WHERE t.IsSpecializedTraining = 0
                        AND st.StaffID = %s
                        AND sc.StartDate <= NOW()
                    GROUP BY t.TrainingName, sc.ScheduleID
                    ORDER BY COUNT(b.MemberID), SUM(b.IsAttended)'''
                parameter = (select_trainerID, )
                db.execute(sql, parameter)
                gc_list = db.fetchall()
                cols_name = [desc[0] for desc in db.description]
                return render_template("/manager/gc_info.html", db_result = gc_list, db_cols = cols_name, all_trainer = all_trainer)
            else:
                db = get_db()
                sql = '''
                    SELECT 
                        sc.StartDate AS "Date",
                        sc.StartTime AS "Start Time",
                        sc.EndTime AS "End Time",
                        t.TrainingName AS "Class Name",
                        CONCAT(st.Firstname, " ", st.Lastname) AS "Trainer Name",
                        COUNT(b.MemberID) AS "Booking Count",
                        IFNULL(SUM(b.IsAttended), 0) AS "Attendance Count"
                    FROM Schedule sc
                    JOIN Training t USING (TrainingID) 
                    JOIN Staff st USING (StaffID)
                    LEFT JOIN Booking b USING (ScheduleID)
                    WHERE t.IsSpecializedTraining = 0
                        AND sc.StartDate <= NOW()
                    GROUP BY t.TrainingName, sc.ScheduleID
                    ORDER BY COUNT(b.MemberID), SUM(b.IsAttended)'''
                db.execute(sql)
                gc_list = db.fetchall()
                cols_name = [desc[0] for desc in db.description]
                return render_template("/manager/gc_info.html", db_result = gc_list, db_cols = cols_name, all_trainer = all_trainer)

    
@bp.route("/class/specializedtraining", methods = ["GET", "POST"])
@manager_required # this function need login first\
def st():
    """Show the specialized training sessions based on the trainer selected."""
    all_trainer = alltrainer()
    select_trainerID = request.form.get('trainerID')
    if select_trainerID is not None:
        db = get_db()
        sql = '''
            SELECT 
                sc.StartDate AS "Date",
                sc.StartTime AS "Start Time",
                sc.EndTime AS "End Time",
                CONCAT(st.Firstname, " ", st.Lastname) AS "Trainer Name",
                t.TrainingName AS "Class Name",
                sc.Room,
                CASE 
                    WHEN b.IsAttended = 1 THEN "Attended"
                    WHEN b.IsAttended = 0 THEN "Absent"
                    ELSE "No booking"
                END AS "Booking/Attendance Status"
            FROM Schedule sc
            JOIN Training t USING (TrainingID) 
            JOIN Staff st USING (StaffID)
            LEFT JOIN Booking b USING (ScheduleID)
            WHERE t.IsSpecializedTraining = 1
                AND st.StaffID = %s
                AND sc.StartDate <= NOW()
            ORDER BY sc.StartDate, sc.StartTime'''
        parameter = (select_trainerID, )
        db.execute(sql, parameter)
        st_list = db.fetchall()
        column_names = [desc[0] for desc in db.description]
        print(st_list)
        return render_template("/manager/st_info.html", db_result = st_list, db_cols = column_names, all_trainer = all_trainer)
    
    else:
        db = get_db()
        sql = '''
            SELECT 
                sc.StartDate AS "Date",
                sc.StartTime AS "Start Time",
                sc.EndTime AS "End Time",
                CONCAT(st.Firstname, " ", st.Lastname) AS "Trainer Name",
                t.TrainingName AS "Class Name",
                sc.Room,
                CASE 
                    WHEN b.IsAttended = 1 THEN "Attended"
                    WHEN b.IsAttended = 0 THEN "Absent"
                    ELSE "No booking"
                END AS "Booking/Attendance Status"
            FROM Schedule sc
            JOIN Training t USING (TrainingID) 
            JOIN Staff st USING (StaffID)
            LEFT JOIN Booking b USING (ScheduleID)
            WHERE t.IsSpecializedTraining = 1
                AND sc.StartDate <= NOW()
            ORDER BY sc.StartDate, sc.StartTime'''
        db.execute(sql)
        st_list = db.fetchall()
        column_names = [desc[0] for desc in db.description]
        return render_template("/manager/st_info.html", db_result = st_list, db_cols = column_names, all_trainer = all_trainer)
