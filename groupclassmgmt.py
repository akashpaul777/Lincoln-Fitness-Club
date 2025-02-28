from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from datetime import datetime, timedelta
from flask import url_for
from auth import manager_required
from db import get_db

bp = Blueprint("groupclassmgmt", __name__, url_prefix="/management/groupclassmgmt")

@bp.route("/groupclass", methods=["GET","POST"])
@manager_required # if this function need manager login first
def training():
    if request.method == 'GET':
        db = get_db()
        db.execute("SELECT * FROM Training where IsClass = 1;")
        traininginfo = db.fetchall()
        return render_template("manager/groupclass/training.html", traininginfo = traininginfo)

    elif request.method == 'POST':
        trname = request.form.get('trname')
        trintro = request.form.get('trintro')
        db = get_db()
        db.execute("""INSERT INTO Training (TrainingName, TrainingInfo, IsSpecializedTraining, IsClass) VALUES(%s,%s,0,1);""",
                (trname,trintro,))
        flash('The group class has been added!')
        return redirect("/management/groupclassmgmt/groupclass")

@bp.route("/")
@bp.route("/schedule")
@manager_required # if this function need manager login first
def listSchedule():
        db = get_db()
        db.execute("SELECT * FROM Schedule join Training on Training.TrainingID = Schedule.TrainingID join Staff on Staff.StaffID = Schedule.StaffID where Training.IsClass = 1 and StartDate > DATE_SUB(NOW(), INTERVAL 7 DAY) order by StartDate asc, StartTime asc;")
        schduleinfo = db.fetchall()
        #print(schduleinfo)
        return render_template("manager/groupclass/schedule.html", schduleinfo = schduleinfo)


@bp.route("/schedule/add", methods=["GET","POST"])
@manager_required # if this function need manager login first
def addSchedule():
        if request.method == 'GET':
                todaydate = datetime.now().date() + timedelta(days=1)
                db = get_db()
                db.execute("SELECT * FROM Training WHERE IsClass = 1 ")
                trainings = db.fetchall()
                db.execute("SELECT * FROM Staff WHERE IsTrainer = 1 ")
                trainers = db.fetchall()
                return render_template("manager/groupclass/addschedule.html", todaydate = todaydate, trainings = trainings, trainers = trainers)
        
        elif request.method == 'POST':
                trainingid = request.form.get('trainingid')
                trainerid = request.form.get('trainerid')
                startdate = request.form.get('startdate')
                startdate = datetime.strptime(startdate,'%Y-%m-%d')
                starttime = request.form.get('starttime')
                duration = request.form.get('duration')
                #format times
                starttime = datetime.strptime(starttime,'%H:%M')
                starttime_timedelta = timedelta(hours=starttime.hour, minutes=starttime.minute, seconds=starttime.second)
                starttime_display = starttime.strftime('%H:%M:%S')
                duration = datetime.strptime(duration, '%H:%M:%S')
                endtime = (starttime + timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second)).time()
                endtime_timedelta = timedelta(hours=endtime.hour, minutes=endtime.minute, seconds=endtime.second)
                endtime_display = endtime.strftime('%H:%M:%S')
                maxcap = request.form.get('maxcap')
                room = request.form.get('room')
                db = get_db()
                db.execute("SELECT StartDate, StartTime, EndTime FROM Schedule WHERE Staffid = %s",(trainerid,))
                existschedules = db.fetchall()
                for existschedule in existschedules:
                    if startdate.year == existschedule[0].year and startdate.month == existschedule[0].month and startdate.day == existschedule[0].day:
                          if (starttime_timedelta < existschedule[1] and endtime_timedelta > existschedule[1]) or (starttime_timedelta >= existschedule[1] and endtime_timedelta <= existschedule[2]) or (starttime_timedelta < existschedule[2] and endtime_timedelta > existschedule[2]):
                                flash('The schedule cannot be added as time overlap with other scheule for this trainer!')
                                return redirect("/management/groupclassmgmt/schedule/add")                   
                          
                db.execute("SELECT StartDate, StartTime, EndTime, Room FROM Schedule")
                allchedules = db.fetchall()
                for allchedule in allchedules:
                    if startdate.year == allchedule[0].year and startdate.month == allchedule[0].month and startdate.day == allchedule[0].day:
                          if (starttime_timedelta < allchedule[1] and endtime_timedelta > allchedule[1]) or (starttime_timedelta >= allchedule[1] and endtime_timedelta <= allchedule[2]) or (starttime_timedelta < allchedule[2] and endtime_timedelta > allchedule[2]):
                                if room in allchedule[3]:
                                        flash('The schedule could not be added as the room not available during this time')
                                        return redirect("/management/groupclassmgmt/schedule/add")        
                                           
                          
                db.execute("""INSERT INTO Schedule (StaffID,TrainingID,Room,StartDate,StartTime,EndTime,DurationInMinutes,MaxCapacity) VALUES (%s,%s,%s,%s,%s,%s,%s,%s); """,
                (trainerid,trainingid,room,startdate,starttime_display,endtime_display,duration,maxcap,))
                flash('The schedule has been added!')
                return redirect("/management/groupclassmgmt/schedule")

@bp.route("/schedule/edit", methods=["POST"])
@manager_required # if this function need manager login first
def editSchedule():
        scheduleid = request.form.get('scheduleid')
        todaydate = datetime.now().date() + timedelta(days=1)
        db = get_db()
        db.execute("Select * FROM Booking WHERE ScheduleID = %s;",(scheduleid,))
        bookinginfo = db.fetchall()
        if bookinginfo:
           flash('This schedule cannot be updated as someone already booked it.')
           return redirect(url_for("groupclassmgmt.listSchedule"))
        else:
           db.execute("SELECT * FROM Schedule join Training on Training.TrainingID = Schedule.TrainingID join Staff on Staff.StaffID = Schedule.StaffID where Schedule.ScheduleID = %s",(scheduleid,))
           schduleinfo = db.fetchall()
           db.execute("SELECT * FROM Staff WHERE IsTrainer = 1 ")
           trainers = db.fetchall()
           return render_template("manager/groupclass/editschedule.html", schduleinfo = schduleinfo, trainers = trainers, todaydate = todaydate)

@bp.route("/schedule/update", methods=["POST"])
@manager_required # if this function need manager login first
def updateSchedule():
        scheduleid = request.form.get('scheduleid')
        trainerid = request.form.get('trainerid')
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
        maxcap = request.form.get('maxcap')
        db = get_db()
        db.execute("SELECT StartDate, StartTime, EndTime FROM Schedule WHERE Staffid = %s and ScheduleID <> %s;",(trainerid,scheduleid,))
        existschedules = db.fetchall()
        for existschedule in existschedules:
                if startdate.year == existschedule[0].year and startdate.month == existschedule[0].month and startdate.day == existschedule[0].day:
                        if (starttime_timedelta < existschedule[1] and endtime_timedelta > existschedule[1]) or (starttime_timedelta >= existschedule[1] and endtime_timedelta <= existschedule[2]) or (starttime_timedelta < existschedule[2] and endtime_timedelta > existschedule[2]):
                                flash('The schedule cannot be added as time overlap with other schedules!')
                                return redirect("/management/groupclassmgmt/schedule")                   
                          
        db.execute("SELECT StartDate, StartTime, EndTime, Room FROM Schedule where ScheduleID <> %s",(scheduleid,))
        allchedules = db.fetchall()
        for allchedule in allchedules:
                if startdate.year == allchedule[0].year and startdate.month == allchedule[0].month and startdate.day == allchedule[0].day:
                        if (starttime_timedelta < allchedule[1] and endtime_timedelta > allchedule[1]) or (starttime_timedelta >= allchedule[1] and endtime_timedelta <= allchedule[2]) or (starttime_timedelta < allchedule[2] and endtime_timedelta > allchedule[2]):
                                if room in allchedule[3]:
                                        flash('The schedule cannot be added as the room not available during this time')
                                        return redirect("/management/groupclassmgmt/schedule")  
                                   
        db.execute("""UPDATE Schedule SET StartDate = %s, StartTime = %s, 
                 Room = %s, EndTime = %s, DurationInMinutes = %s, MaxCapacity = %s WHERE ScheduleID = %s;""",
                (startdate,starttime,room,endtime,duration,maxcap,scheduleid,))
        flash('The changes has been saved!')
        return redirect("/management/groupclassmgmt/schedule")

@bp.route("/schedule/del", methods=["POST"])
@manager_required # if this function need manager login first
def delSchedule():
        scheduleid = request.form.get('scheduleid')
        db = get_db()
        db.execute("Select * FROM Booking WHERE ScheduleID = %s;",(scheduleid,))
        bookinginfo = db.fetchall()
        if bookinginfo:
           flash('This schedule cannot be deleted as someone already booked it. Please cancel the booking first!')
        else:
           db.execute("DELETE FROM Schedule WHERE ScheduleID = %s;",(scheduleid,))
           flash('The group schedule has been deleted!')
        return redirect("/management/groupclassmgmt/schedule")