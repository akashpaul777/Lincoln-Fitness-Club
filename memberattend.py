from flask import Blueprint
from flask import flash
from flask import g
from flask import render_template
from flask import request
from db import get_db

bp = Blueprint("memberattend", __name__, url_prefix="/member")


@bp.route("/attend", methods=("POST", "GET"), endpoint='member_attend')
def attend():
    if request.method == 'GET':
        return render_template('member/memberattend.html')
    member_id = request.form.get('memberId')
    query_user_sql = 'SELECT isActive from Member WHERE MemberID=%s'
    db = get_db()
    db.execute(query_user_sql, (member_id,))
    user = db.fetchone()
    if not user:
        flash(f'Member ID {member_id} is not exist.')
        return render_template('member/memberattend.html')
    if not user[0]:
        flash('Your account is not active')
        return render_template('member/memberattend.html')
    query_sql = """
        SELECT Booking.BookingID, Booking.IsAttended
        FROM Booking
        INNER JOIN Schedule ON Booking.ScheduleID = Schedule.ScheduleID
        WHERE Booking.MemberID = %s
        AND NOW() BETWEEN CONCAT(Schedule.StartDate, ' ', Schedule.StartTime) AND CONCAT(Schedule.StartDate, ' ', Schedule.EndTime);
    """
    db.execute(query_sql, (member_id,))
    book_data = db.fetchone()
    if book_data:
        attend_sql = """
        UPDATE Booking SET IsAttended = 1 WHERE BookingID=%s AND MemberID=%s
        """
        db.execute(attend_sql, (book_data[0], member_id))
        g.connection.commit()
        flash('Check in is successfully!' if book_data[1] == 0 else 'You have already Checked in.')
    else:
        db.execute("""INSERT INTO Normalvisit (MemberID,AttendDate) VALUES ( %s, NOW());""",(member_id,))
        flash('Welcome to use the facility!')
    return render_template('member/memberattend.html')

