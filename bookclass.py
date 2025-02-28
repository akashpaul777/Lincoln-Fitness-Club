from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from datetime import datetime, timedelta, date
from auth import member_required
from db import get_db
import base64

bp = Blueprint("bookclass", __name__, url_prefix="/member/bookclass")

# formatted_current_time is current date and time
today = date.today()
now = datetime.now()
current_date_time = now.strftime("%Y-%m-%d %H:%M:%S")

def alltrainer():
    db = get_db()
    db.execute('SELECT CONCAT(Firstname, " ", Lastname) AS "Trainer Name" FROM Staff WHERE IsTrainer = 1')
    all_trainer = db.fetchall()
    return all_trainer

@bp.route("/", methods = ["GET", "POST"])
@member_required # this function need login first
def classtype():
    return render_template("/member/classtype.html")

@bp.route("/classlist", methods = ["GET", "POST"])
@member_required # this function need login first
def selectclass():
    # validate if the member's account is currently active or not before book class
    if request.method == "POST":
        class_type = request.form.get('class_type')
        IsSpecializedTraining = ""
        if g.user.membershipEndDate > today:
            if class_type == "specialized training":
                return redirect(url_for("bookclass.select_trainer"))
            
            elif class_type == "group class":
                IsSpecializedTraining = 0
                db = get_db()
                sql = '''
                    SELECT 
                    	sc.ScheduleID,
                        t.TrainingName AS "Class Name",
                        CONCAT(st.Firstname, " ", st.Lastname) AS "Trainer Name",
                        sc.StartDate AS "Date",
                        sc.StartTime AS "Start Time",
                        sc.EndTime  AS "End Time",
                        sc.DurationInMinutes AS "Session In Minutes",
                        sc.Room,
                        sc.MaxCapacity-count(b.memberid) as "RemainingSeat",
                        t.TrainingInfo,
                        st.Introduction
                    FROM Schedule sc
                    LEFT JOIN Training t USING (TrainingID) 
                    LEFT JOIN Staff st USING (StaffID)
                    LEFT JOIN Booking b USING (ScheduleID)
                    WHERE t.IsSpecializedTraining = %s
                        AND %s <= ADDTIME(sc.StartDate, sc.StartTime)
                        AND ADDTIME(sc.StartDate, sc.StartTime) < %s
                    GROUP BY sc.ScheduleID
                    ORDER BY sc.StartDate, sc.StartTime;'''
                parameters = (IsSpecializedTraining, current_date_time, g.user.membershipEndDate)
                db.execute(sql, parameters)
                class_list = db.fetchall()
                column_names = [desc[0] for desc in db.description]
                return render_template('member/groupclass.html', db_result = class_list, db_cols = column_names)
        else:
            flash("Your membership is expired, please contact us to renew it before booking a class.")
            return redirect(url_for('bookclass.classtype'))
    else:
        return redirect(url_for("bookclass.classtype"))
    

@bp.route("/classlist/select_trainer", methods = ["GET", "POST"])
def select_trainer():
    IsSpecializedTraining = 1
    all_trainer = alltrainer()
    select_trainername = request.form.get('trainername')
    db = get_db()
    db.row_factory.execute("Select * from Member where MemberID = %s", (g.user.id,))
    member = db.row_factory.fetchone()
    try:
        member['CardNumber'] = base64.b64decode(member['CardNumber']).decode('utf-8')
    except Exception:
        member['CardNumber'] = member['CardNumber']
    member['CardNumber'] = '************' + member['CardNumber'][12:]
    if select_trainername is not None:
        sql = '''
                SELECT 
                    sc.ScheduleID AS "Class ID",
                    t.TrainingName AS "Session Name",
                    CONCAT(st.Firstname, " ", st.Lastname) AS "Trainer Name",
                    sc.StartDate AS "Date",
                    sc.StartTime AS "Start Time",
                    sc.EndTime AS "End Time",
                    sc.DurationInMinutes AS "Session In Minutes",
                    sc.Room,
                    p.Value as Fee,
                    p.PriceID AS PriceID,
                    t.TrainingInfo,
                    st.Introduction
                FROM Schedule sc
                JOIN Training t USING (TrainingID) 
                JOIN Staff st USING (StaffID)
                JOIN Price p USING (PriceID)
                WHERE t.IsSpecializedTraining = %s 
                    AND CONCAT(st.Firstname, " ", st.Lastname) = %s
                    AND sc.ScheduleID NOT IN (SELECT ScheduleID FROM Booking) 
                    AND %s <= ADDTIME(sc.StartDate, sc.StartTime)
                    AND ADDTIME(sc.StartDate, sc.StartTime) < %s
                ORDER BY sc.StartDate, sc.StartTime'''
        parameters = (IsSpecializedTraining, select_trainername, current_date_time, g.user.membershipEndDate)
        db.execute(sql, parameters)
        class_list = db.fetchall()
        column_names = [desc[0] for desc in db.description]
        return render_template('/member/specializedtraining.html', db_result = class_list, db_cols = column_names, all_trainer = all_trainer, member=member)
    else:    
        db = get_db()
        sql = '''
                SELECT 
                    sc.ScheduleID AS "Class ID",
                    t.TrainingName AS "Session Name",
                    CONCAT(st.Firstname, " ", st.Lastname) AS "Trainer Name",
                    sc.StartDate AS "Date",
                    sc.StartTime AS "Start Time",
                    sc.EndTime AS "End Time",
                    sc.DurationInMinutes AS "Session In Minutes",
                    sc.Room,
                    p.Value as Fee,
                    p.PriceID AS PriceID,
                    t.TrainingInfo,
                    st.Introduction
                FROM Schedule sc
                JOIN Training t USING (TrainingID) 
                JOIN Staff st USING (StaffID)
                JOIN Price p USING (PriceID)
                WHERE t.IsSpecializedTraining = %s 
                    AND sc.ScheduleID NOT IN (SELECT ScheduleID FROM Booking) 
                    AND %s <= ADDTIME(sc.StartDate, sc.StartTime)
                    AND ADDTIME(sc.StartDate, sc.StartTime) < %s
                ORDER BY sc.StartDate, sc.StartTime'''
        parameters = (IsSpecializedTraining, current_date_time, g.user.membershipEndDate)
        db.execute(sql, parameters)
        class_list = db.fetchall()
        column_names = [desc[0] for desc in db.description]
        return render_template('/member/specializedtraining.html', db_result = class_list, db_cols = column_names, all_trainer = all_trainer, member=member)


# User Story NO.8
@bp.route("/classlist/select_trainer/bookst", methods = ["GET", "POST"])
@member_required # this function need login first
def bookst():
    specialized_training_id = request.form.get('specialized_training_id')
    specialized_training_start_date = request.form.get('specialized_training_start_date')
    specialized_training_start_time = request.form.get('specialized_training_start_time')
    specialized_training_end_time = request.form.get('specialized_training_end_time')
    specialized_training_fee = request.form.get('specialized_training_fee')
    specialized_training_price_id = request.form.get('specialized_training_price_id')
    specialized_training_name = request.form.get('specialized_training_name')
    start_datetime_str = specialized_training_start_date + " " + specialized_training_start_time
    end_datetime_str = specialized_training_start_date + " " + specialized_training_end_time
    selected_st_start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
    selected_st_end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')
    # Get all my bookings
    db = get_db()
    db.row_factory.execute(
    """SELECT s.ScheduleID, s.StartDate, s.StartTime, s.EndTime FROM Booking 
    INNER join Schedule s on s.ScheduleID = Booking.ScheduleID
    where MemberID = '%s' and Booking.IsAttended != 1;""", (g.user.id, ))
    all_bookings = db.row_factory.fetchall()
    # Compare the selected sTrainngSession with all the booked sTrainingSessions
    is_not_overlapped = True
    for booking in all_bookings:
        start_datetime = datetime.combine(booking['StartDate'], datetime.min.time()) + booking['StartTime']
        end_datetime = datetime.combine(booking['StartDate'], datetime.min.time()) + booking['EndTime']
        is_not_overlapped = check_events_no_overlap(selected_st_start_datetime, selected_st_end_datetime, start_datetime, end_datetime)
        if is_not_overlapped == False:
            break
    if is_not_overlapped == False:
        flash(f"""{specialized_training_name} overlap with other bookings. Please select another training session.""")
        return redirect(url_for("bookclass.list_bookings"))
    #No conflicts do payment and booking
    #payment
    sql_creat_payment = """
        INSERT INTO Payment 
        (Value,MemberID,ScheduleID,PaymentDate,PriceID)
        VALUES(%s,%s,%s,%s,%s)
    """
    db.execute(sql_creat_payment, (
        specialized_training_fee,
        g.user.id,
        specialized_training_id,
        datetime.today().strftime('%Y-%m-%d'),
        specialized_training_price_id
    ))
    #Booking
    insert_sql = "INSERT INTO Booking (ScheduleID, MemberID, IsAttended) VALUES (%s,%s,%s)"
    insert_data = [specialized_training_id, g.user.id, 0]
    db = get_db()
    db.execute(insert_sql, insert_data)
    flash (f"""{specialized_training_name} has been paid and booked successfully!""")
    return redirect(url_for("bookclass.list_bookings"))
    # randomly pick an url_for to keep running after completing us-2 in Sprint 1

def check_events_no_overlap(startA, endA, startB, endB):
    return endA <= startB or endB <= startA

# User Story NO.7
@bp.route("/classlist/bookgc", methods = ["GET", "POST"])
@member_required # this function need login first
def bookgc():
    scheduleid = request.form.get('scheduleid')
    remainseat = int(request.form.get('remainseat'))
    isattended="0"
    startdate = request.form.get('startdate')
    startdate = datetime.strptime(startdate,'%Y-%m-%d')
    starttime1 = request.form.get('starttime')
    duration = request.form.get('duration')
                #format times
    starttime = datetime.strptime(starttime1,'%H:%M:%S')
    starttime_timedelta = timedelta(hours=starttime.hour, minutes=starttime.minute, seconds=starttime.second)
        #starttime_display = starttime.strftime('%H:%M:%S')
    duration = datetime.strptime(duration, '%H:%M:%S')
    endtime = (starttime + timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second)).time()
    endtime_timedelta = timedelta(hours=endtime.hour, minutes=endtime.minute, seconds=endtime.second)
    if request.method == 'POST':
        
        #endtime_display = starttime.strftime('%H:%M:%S')
        db = get_db()   
 
        db.execute("SELECT StartDate, StartTime, EndTime FROM Schedule join Booking USING (ScheduleID) WHERE memberid = %s",(g.user.id,))
        existschedules = db.fetchall()
        for existschedule in existschedules:
            if startdate.year == existschedule[0].year and startdate.month == existschedule[0].month and startdate.day == existschedule[0].day:
                    if (starttime_timedelta < existschedule[1] and endtime_timedelta > existschedule[1]) or (starttime_timedelta >= existschedule[1] and endtime_timedelta <= existschedule[2]) or (starttime_timedelta < existschedule[2] and endtime_timedelta > existschedule[2]):
                                flash('The class cannot be added as there is time conflict!')
                                return redirect(url_for("bookclass.list_bookings"))                    
        if remainseat>0:
            db.execute("Insert into Booking (scheduleid,memberid,isattended) values (%s,%s,%s)",(scheduleid,g.user.id,isattended,))   
            flash('Group Class booked successfully!')         
            return redirect(url_for("bookclass.list_bookings")) 
    else:
       
        return redirect("/member/bookclass/classlist")

@bp.route("/classlist/bookings", methods = ["GET"])
def list_bookings():
    sql = """
        SELECT
        s.StartDate, 
        s.StartTime, 
        s.EndTime, 
        s.Room, 
        t.TrainingName
        FROM Booking b
        INNER join Schedule s on s.ScheduleID = b.ScheduleID
        INNER join Training t on t.TrainingID = s.TrainingID
        where MemberID = %s and s.StartDate >= CURDATE()
        order by s.StartDate asc, s.StartTime asc;
    """
    parameters = (g.user.id,)
    db = get_db()
    db.execute(sql, parameters)
    booking_list = db.fetchall()
    column_names = [desc[0] for desc in db.description]
    return render_template('/member/listbookings.html', db_result = booking_list, db_cols = column_names)

@bp.route("/classlist/bookings/history", methods = ["GET"])
def booking_history():
    sql = """
        SELECT
        s.StartDate, 
        s.StartTime, 
        s.EndTime, 
        s.Room, 
        t.TrainingName
        FROM Booking b
        INNER join Schedule s on s.ScheduleID = b.ScheduleID
        INNER join Training t on t.TrainingID = s.TrainingID
        where MemberID = %s and s.StartDate < CURDATE()
        order by s.StartDate desc, s.StartTime desc;
    """
    parameters = (g.user.id,)
    db = get_db()
    db.execute(sql, parameters)
    booking_list = db.fetchall()
    column_names = [desc[0] for desc in db.description]
    return render_template('/member/bookinghistory.html', db_result = booking_list, db_cols = column_names)