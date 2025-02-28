from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from auth import login_required, manager_required
from db import get_db

bp = Blueprint("popularclasses", __name__, url_prefix="/management/popularclasses")


@bp.route("/classes", methods=["GET"])
@manager_required
def classes():
    class_type = request.args.get('class_type')
    sql = """SELECT 
    TrainingName as "Name",
    (   select count(*) 
        from Booking b 
        join Schedule s on b.ScheduleID = s.ScheduleID 
        where s.TrainingID = t.TrainingID
    ) as Booking,
    (   select count(*) 
        from Booking b 
        join Schedule s on b.ScheduleID = s.ScheduleID 
        where s.TrainingID = t.TrainingID and b.IsAttended = 1
    ) as Attendance
    from Training t where t.IsClass = %s order by Attendance desc, Booking desc;"""
    db = get_db()
    db.execute(sql, ((0 if class_type =="specialized_training_session" else 1),))
    list = db.fetchall()
    column_names = [desc[0] for desc in db.description]
    return render_template("manager/groupclass/popularclasses.html", db_result = list, db_cols=column_names, class_type=class_type)