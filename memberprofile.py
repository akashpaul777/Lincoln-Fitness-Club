from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
import datetime

from auth import member_required
from db import get_db

bp = Blueprint("memberprofile", __name__, url_prefix="/member/profile")

# formatted_current_time is current date and time
today = datetime.date.today()
today_str = today.strftime('%Y-%m-%d')
seven_days_before = today - datetime.timedelta(days=7)
seven_days_before_str = seven_days_before.strftime('%Y-%m-%d')

@bp.route("/")
@member_required # if this function need login first
def getmember():
  db = get_db()
  db.execute("select memberid,FirstName, LastName, Gender, DayofBirth, email, phonenumber, healthcondition, housenumbername as HouseNumber, street, town, city, postalcode, membershipstartdate, membershipenddate,t.term\
                from Member m \
                inner join MembershipTerm t\
                on m.membershipterm=t.membershiptermid\
                where memberid =%s",(g.user.id,))      
  memberinfo = db.fetchall()
  return render_template("member/memberprofile.html", memberinfo = memberinfo)


@bp.route('/update', methods=['GET','POST'])
@member_required
def memberUpdate():
  if request.method == 'POST':
    memberid = request.form.get('memberid')
    email = request.form.get('email')
    phonenumber=request.form.get('phonenumber')
    healthcondition=', '.join(request.form.getlist('healthcondition'))
    print(healthcondition)
    housenumbername = request.form.get('housenumbername')
    street = request.form.get('street')
    town = request.form.get('town')
    city = request.form.get('city')
    postalcode = request.form.get('postalcode')
    db = get_db()
    db.execute("UPDATE Member SET email=%s, PhoneNumber=%s, HealthCondition=%s, HouseNumberName=%s, Street=%s, Town=%s,City=%s, Postalcode=%s \
                where MemberID=%s",(email, phonenumber,healthcondition,housenumbername,street,town,city,postalcode,memberid,))
    
    flash('The change has been saved!')
    return redirect("/member/profile/update")
  
    
  elif request.method == 'GET':
    db = get_db()
    db.execute("select MemberID,FirstName, LastName, Gender, DayofBirth, Email, PhoneNumber, HealthCondition, HouseNumberName, Street, Town, City, Postalcode\
                 from Member\
                 where memberid =%s",(g.user.id,))
    memberinfo = db.fetchall()
    return render_template('member/memberupdate.html',memberinfo = memberinfo)


# showing payment history
@bp.route('/payment')  
@member_required
def payment_history():
  db = get_db()
  sql = '''
      SELECT 
        CONCAT(m.Firstname, " ", m.Lastname) AS "Member Name",
        p.PaymentDate AS "Payment Date",
        p.Value,
        CASE pr.Name 
            WHEN "Yearly" THEN "Yearly membership fee"
            WHEN "Monthly" THEN "Monthly membership fee"
            ELSE "Special Training fee"
        END AS "Pay For"
      FROM Member m
      JOIN Payment p USING (MemberID)
      JOIN Price pr USING (PriceID)
      WHERE MemberID = %s
      ORDER BY p.PaymentDate DESC
    '''
  db.execute(sql, (g.user.id,))
  payment_history = db.fetchall()
  payment_history_cols = [desc[0] for desc in db.description]
  return render_template("member/payment.html", payment_result = payment_history, payment_cols = payment_history_cols)

    

    
    
    
 
    


