from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from datetime import datetime, timedelta
from auth import login_required, trainer_required
from db import get_db

bp = Blueprint("trainingmgmt", __name__, url_prefix="/trainer/trainingmgmt")

@bp.route("/training", methods=["GET","POST"])
@trainer_required # if this function need trainer login first
def training():
    if request.method == 'GET':
        db = get_db()
        db.execute("SELECT * FROM Training where IsSpecializedTraining = 1;")
        traininginfo = db.fetchall()
        return render_template("trainer/training.html", traininginfo = traininginfo)

    elif request.method == 'POST':
        trname = request.form.get('trname')
        trintro = request.form.get('trintro')
        db = get_db()
        db.execute("""INSERT INTO Training (TrainingName, TrainingInfo, IsSpecializedTraining, IsClass) VALUES(%s,%s,1,0);""",
                (trname,trintro,))
        flash('The specialized training has been added!')
        return redirect("/trainer/trainingmgmt/training")

@bp.route("/")
@bp.route("/schedule")
@trainer_required # if this function need trainer login first
def listSchedule():
        db = get_db()
        db.execute("SELECT * FROM Schedule join Training on Training.TrainingID = Schedule.TrainingID where Schedule.StaffID = %s and Training.IsSpecializedTraining = 1 and StartDate >= CURDATE() order by StartDate asc, StartTime asc;",(g.user.id,))
        schduleinfo = db.fetchall()
        #print(schduleinfo)
        return render_template("trainer/schedule.html", schduleinfo = schduleinfo)

@bp.route("/traineelist")
@trainer_required # if this function need trainer login first
def TraineeList():
        db = get_db()
        db.execute("SELECT * FROM Schedule join Training on Training.TrainingID = Schedule.TrainingID where Schedule.StaffID = %s and StartDate >= CURDATE() order by StartDate asc, StartTime asc;",(g.user.id,))
        schduleinfo = db.fetchall()
        #print(schduleinfo)
        return render_template("trainer/traineeslist.html", schduleinfo = schduleinfo)



@bp.route("/schedule/add", methods=["GET","POST"])
@trainer_required # if this function need trainer login first
def addSchedule():
        if request.method == 'GET':
                todaydate = datetime.now().date() + timedelta(days=1)
                db = get_db()
                db.execute("SELECT * FROM Training WHERE IsSpecializedTraining = 1 ")
                trainings = db.fetchall()
                db.execute("SELECT * FROM Price WHERE IsMembershipterm = 0 ")
                prices = db.fetchall()
                return render_template("trainer/addschedule.html", todaydate = todaydate, prices = prices, trainings = trainings)
        
        elif request.method == 'POST':
                trainingid = request.form.get('trainingid')
                priceid = request.form.get('priceid')
                startdate = request.form.get('startdate')
                startdate = datetime.strptime(startdate,'%Y-%m-%d')
                starttime1 = request.form.get('starttime')
                duration = request.form.get('duration')
                #format times
                starttime = datetime.strptime(starttime1,'%H:%M')
                starttime_timedelta = timedelta(hours=starttime.hour, minutes=starttime.minute, seconds=starttime.second)
                starttime_display = starttime.strftime('%H:%M:%S')
                duration = datetime.strptime(duration, '%H:%M:%S')
                endtime = (starttime + timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second)).time()
                endtime_timedelta = timedelta(hours=endtime.hour, minutes=endtime.minute, seconds=endtime.second)
                endtime_display = endtime.strftime('%H:%M:%S')
                
                room = request.form.get('room')
                db = get_db()
                db.execute("SELECT StartDate, StartTime, EndTime FROM Schedule WHERE Staffid = %s",(g.user.id,))
                existschedules = db.fetchall()
                for existschedule in existschedules:
                    if startdate.year == existschedule[0].year and startdate.month == existschedule[0].month and startdate.day == existschedule[0].day:
                          if (starttime_timedelta < existschedule[1] and endtime_timedelta > existschedule[1]) or (starttime_timedelta >= existschedule[1] and endtime_timedelta <= existschedule[2]) or (starttime_timedelta < existschedule[2] and endtime_timedelta > existschedule[2]):
                                flash('The schedule cannot be added as time overlap with others!')
                                return redirect("/trainer/trainingmgmt/schedule/add")                   
                          
                db.execute("SELECT StartDate, StartTime, EndTime, Room FROM Schedule")
                allchedules = db.fetchall()
                for allchedule in allchedules:
                    if startdate.year == allchedule[0].year and startdate.month == allchedule[0].month and startdate.day == allchedule[0].day:
                          if (starttime_timedelta < allchedule[1] and endtime_timedelta > allchedule[1]) or (starttime_timedelta >= allchedule[1] and endtime_timedelta <= allchedule[2]) or (starttime_timedelta < allchedule[2] and endtime_timedelta > allchedule[2]):
                                if room in allchedule[3]:
                                        flash('The schedule cannot be added as the room not available during this time')
                                        return redirect("/trainer/trainingmgmt/schedule/add")        
                                           
                          
                db.execute("""INSERT INTO Schedule (StaffID,TrainingID,Room,PriceID,StartDate,StartTime,EndTime,DurationInMinutes,MaxCapacity) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,1); """,
                (g.user.id,trainingid,room,priceid,startdate,starttime_display,endtime_display,duration,))
                flash('The schedule has been added!')
                return redirect("/trainer/trainingmgmt/schedule")

@bp.route("/schedule/edit", methods=["POST"])
@trainer_required # if this function need trainer login first
def editSchedule():
        scheduleid = request.form.get('scheduleid')
        todaydate = datetime.now().date() + timedelta(days=1)
        db = get_db()
        db.execute("Select * FROM Booking WHERE ScheduleID = %s;",(scheduleid,))
        bookinginfo = db.fetchall()
        if bookinginfo:
           flash('This schedule cannot be updated as someone already booked it.')
           return redirect(url_for("trainingmgmt.listSchedule"))
        else:
           db.execute("SELECT * FROM Schedule join Training on Training.TrainingID = Schedule.TrainingID where Schedule.ScheduleID = %s;",(scheduleid,))
           schduleinfo = db.fetchall()
           return render_template("trainer/editschedule.html", schduleinfo = schduleinfo, todaydate = todaydate)

@bp.route("/schedule/update", methods=["POST"])
@trainer_required # if this function need trainer login first
def updateSchedule():
        scheduleid = request.form.get('scheduleid')
        startdate = request.form.get('startdate')
        starttime = request.form.get('starttime')
        duration = request.form.get('duration')
        #format times
        startdate = datetime.strptime(startdate,'%Y-%m-%d')
        starttime = datetime.strptime(starttime,'%H:%M:%S')
        starttime_timedelta = timedelta(hours=starttime.hour, minutes=starttime.minute, seconds=starttime.second)
        duration = datetime.strptime(duration, '%H:%M:%S')
        endtime = (starttime + timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second)).time()
        endtime_timedelta = timedelta(hours=endtime.hour, minutes=endtime.minute, seconds=endtime.second)
        room = request.form.get('room')
        db = get_db()
        db.execute("SELECT StartDate, StartTime, EndTime FROM Schedule WHERE Staffid = %s and ScheduleID <> %s;",(g.user.id,scheduleid,))
        existschedules = db.fetchall()
        for existschedule in existschedules:
                if startdate.year == existschedule[0].year and startdate.month == existschedule[0].month and startdate.day == existschedule[0].day:
                        if (starttime_timedelta < existschedule[1] and endtime_timedelta > existschedule[1]) or (starttime_timedelta >= existschedule[1] and endtime_timedelta <= existschedule[2]) or (starttime_timedelta < existschedule[2] and endtime_timedelta > existschedule[2]):
                                flash('The schedule cannot be added as time overlap with other schedules!')
                                return redirect("/trainer/trainingmgmt/schedule")                   
                          
        db.execute("SELECT StartDate, StartTime, EndTime, Room FROM Schedule where ScheduleID <> %s",(scheduleid,))
        allchedules = db.fetchall()
        for allchedule in allchedules:
                if startdate.year == allchedule[0].year and startdate.month == allchedule[0].month and startdate.day == allchedule[0].day:
                        if (starttime_timedelta < allchedule[1] and endtime_timedelta > allchedule[1]) or (starttime_timedelta >= allchedule[1] and endtime_timedelta <= allchedule[2]) or (starttime_timedelta < allchedule[2] and endtime_timedelta > allchedule[2]):
                                if room in allchedule[3]:
                                        flash('The schedule cannot be added as the room not available during this time')
                                        return redirect("/trainer/trainingmgmt/schedule")  
                                   
        db.execute("""UPDATE Schedule SET StartDate = %s, StartTime = %s, 
                 Room = %s, EndTime = %s, DurationInMinutes = %s WHERE ScheduleID = %s;""",
                (startdate,starttime,room,endtime,duration,scheduleid,))
        flash('The change has been saved!')
        return redirect("/trainer/trainingmgmt/schedule")

@bp.route("/schedule/del", methods=["POST"])
@trainer_required # if this function need trainer login first
def delSchedule():
        scheduleid = request.form.get('scheduleid')
        db = get_db()
        db.execute("Select * FROM Booking WHERE ScheduleID = %s;",(scheduleid,))
        bookinginfo = db.fetchall()
        if bookinginfo:
           flash('This schedule cannot be deleted as someone already booked it. Please cancel the booking first!')
        else:
           db.execute("DELETE FROM Schedule WHERE ScheduleID = %s;",(scheduleid,))
           flash('The specialized training schedule has been deleted!')
        return redirect("/trainer/trainingmgmt/schedule")

@bp.route("/schedule/trainees")
@trainer_required # if this function need trainer login first
def listTrainees():
        scheduleid = request.args.get('scheduleid')
        db = get_db()
        db.execute("""SELECT m.MemberID, m.Firstname, m.lastname, m.DayOfBirth, b.IsAttended FROM Booking b join Schedule s
        on s.ScheduleID = b.ScheduleID
        join Training t on t.TrainingID = s.TrainingID 
        join Member m on m.MemberID = b.MemberID
        WHERE b.ScheduleID = %s""",(scheduleid,))
        trainees = db.fetchall()
        return render_template("trainer/trainees.html", trainees = trainees, scheduleid = scheduleid)

@bp.route("/schedule/trainees/detail")
@trainer_required # if this function need trainer login first
def traineeDetail():
        traineeID = request.args.get('traineeID')
        db = get_db()
        db.execute("""SELECT * FROM Member WHERE MemberID = %s""",(traineeID,))
        memberinfo = db.fetchall()
        return render_template("trainer/traineeprofile.html", memberinfo = memberinfo)

@bp.route("/schedule/trainees/search")
@trainer_required # if this function need trainer login first
def searchTrainee():
        scheduleid = request.args.get('scheduleid')
        trainee = request.args.get('trainee')
        searchinfo = "%" + trainee + "%"
        db = get_db()
        if trainee:
                db.execute("""SELECT m.MemberID, m.Firstname, m.lastname, m.DayOfBirth FROM Booking b join Schedule s
                on s.ScheduleID = b.ScheduleID
                join Training t on t.TrainingID = s.TrainingID 
                join Member m on m.MemberID = b.MemberID
                WHERE b.ScheduleID = %s and m.Firstname like %s""",(scheduleid, searchinfo,))
                trainees = db.fetchall()
        else:
                db.execute("""SELECT m.MemberID, m.Firstname, m.lastname, m.DayOfBirth FROM Booking b join Schedule s
                on s.ScheduleID = b.ScheduleID
                join Training t on t.TrainingID = s.TrainingID 
                join Member m on m.MemberID = b.MemberID
                WHERE b.ScheduleID = %s """,(scheduleid,))
                trainees = db.fetchall()
                
        return render_template("trainer/trainees.html", trainees = trainees, scheduleid = scheduleid )
