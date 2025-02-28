from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from auth import login_required, manager_required
from db import get_db

bp = Blueprint("userreport", __name__, url_prefix="/manager/userreport")

@bp.route("/")
@manager_required # if this function need manager login first
def index():
    memberid = request.args.get('memberid')
    startdate = request.args.get('date1')
    enddate = request.args.get('date2')
    db = get_db()
    if startdate:
        db.execute("""SELECT Count(MemberID) FROM Normalvisit join Member USING(MemberID) where MemberID = %s and (Normalvisit.AttendDate >= %s AND Normalvisit.AttendDate <= %s);""",(memberid,startdate,enddate,))
        normalvisit = db.fetchone()[0]
        db.execute("""SELECT Count(MemberID) FROM Booking b join Schedule s USING(ScheduleID) join Training t USING(TrainingID) join Member m USING(MemberID) where b.IsAttended = 1 and t.IsClass = 1 and MemberID = %s and (s.StartDate >= %s AND s.StartDate <= %s);""",(memberid,startdate,enddate,))
        groupclassvisit = db.fetchone()[0]
        db.execute("""SELECT Count(MemberID) FROM Booking b join Schedule s USING(ScheduleID) join Training t USING(TrainingID) join Member m USING(MemberID) where b.IsAttended = 1 and t.IsSpecializedTraining = 1 and MemberID = %s and (s.StartDate >= %s AND s.StartDate <= %s);""",(memberid,startdate,enddate,))
        specializedvisit = db.fetchone()[0]
    
    else:
        db.execute("""SELECT Count(MemberID) FROM Normalvisit join Member USING(MemberID) where MemberID = %s;""",(memberid,))
        normalvisit = db.fetchone()[0]
        db.execute("""SELECT Count(MemberID) FROM Booking b join Schedule s USING(ScheduleID) join Training t USING(TrainingID) join Member m USING(MemberID) where b.IsAttended = 1 and t.IsClass = 1 and MemberID = %s""",(memberid,))
        groupclassvisit = db.fetchone()[0]
        db.execute("""SELECT Count(MemberID) FROM Booking b join Schedule s USING(ScheduleID) join Training t USING(TrainingID) join Member m USING(MemberID) where b.IsAttended = 1 and t.IsSpecializedTraining = 1 and MemberID = %s;""",(memberid,))
        specializedvisit = db.fetchone()[0]
    return render_template("manager/user_rpt.html", memberid = memberid, normalvisit = normalvisit, groupclassvisit = groupclassvisit, specializedvisit = specializedvisit, startdate = startdate, enddate = enddate)


