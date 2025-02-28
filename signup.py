from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from datetime import datetime
from dateutil import relativedelta
import json
from auth import login_required, manager_required, trainer_required, no_login_required
from db import get_db
import base64

bp = Blueprint("signup", __name__, url_prefix="/signup")

@bp.route("/", methods=("GET", "POST"))
@no_login_required
def index():
    form_data = {
        "memberid":"",
        "firstname": "",
        "familyname": "",
        "gender": "",
        "date_of_birth": "",
        "email": "",
        "phone_number": "",
        "house": "",
        "street": "",
        "town": "",
        "city": "",
        "postalcode": "",
        "health_conditions": "",
        "membership_term": "",
        "membership_price": "",
        "card_number": "",
        "cvv": "",
        "card_holder_name": "",
        "card_expire": ""
    }
    sql_get_membershipterm = """
        SELECT 
            mst.MembershipTermID,
            mst.Term,
            p.Value,
            p.PriceID
        FROM MembershipTerm mst
        JOIN Price as p on mst.PriceID = p.PriceID;
    """
    db = get_db()
    g.db.row_factory.execute(sql_get_membershipterm)
    membershipterm_list = g.db.row_factory.fetchall()
    if request.method == "POST":
        createMember(form_data)
        return redirect(url_for('index'))
    # flash("Payment failed.")
    return render_template("member/signup.html", membershipterm_list= membershipterm_list, form_data=form_data)

def createMember(form_data):
    form_data["memberid"] = request.form.get('memberid')
    form_data["firstname"] = request.form.get('firstname')
    form_data["familyname"] = request.form.get('familyname')
    form_data["gender"] = request.form.get('gender')
    form_data["date_of_birth"] = request.form.get('dateofbirth')
    form_data["email"] = request.form.get('email')
    form_data["phone_number"] = request.form.get('phonenumber')
    form_data["house"] = request.form.get('house')
    form_data["street"] = request.form.get('street')
    form_data["town"] = request.form.get('town')
    form_data["city"] = request.form.get('city')
    form_data["postalcode"] = request.form.get('postalcode')
    form_data["health_conditions"] = ', '.join(request.form.getlist('health_conditions'))
    membershipterm_json = json.loads(request.form.get('membershipterm').replace("'", '"'))
    form_data["membership_term"] = membershipterm_json['id']
    form_data["membership_price"] = membershipterm_json['value']
    form_data["membership_price_id"] = membershipterm_json['price_id']
    form_data["card_number"] = base64.b64encode(request.form.get('card_number').encode('utf-8')).decode('utf-8') 
    form_data["cvv"] = base64.b64encode(request.form.get('cvv').encode('utf-8')).decode('utf-8')
    form_data["card_holder_name"] = base64.b64encode(request.form.get('card_holder_name').encode('utf-8')).decode('utf-8')
    form_data["card_expire"] =base64.b64encode(request.form.get('card_expire').encode('utf-8')).decode('utf-8')
    current_date = datetime.today()
    until_date = current_date + relativedelta.relativedelta(months=1)
    if membershipterm_json['term'].lower().find("year") != -1 :
        until_date = current_date + relativedelta.relativedelta(years=1)
    if form_data["memberid"] == "":
        sql_creat_member = """
            INSERT INTO Member 
            (Firstname,Lastname,Gender,DayOfBirth,Email,PhoneNumber,
            HealthCondition,HouseNumberName,Street,Town,City,Postalcode,
            MembershipStartDate,MembershipEndDate,MembershipTerm,IsActive,
            CardNumber,CVV,CardExpiry,NameOnCard)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        g.db.execute(sql_creat_member, (
            form_data["firstname"],
            form_data["familyname"],
            form_data["gender"],
            form_data["date_of_birth"],
            form_data["email"],
            form_data["phone_number"],
            form_data["health_conditions"],
            form_data["house"],
            form_data["street"],
            form_data["town"],
            form_data["city"],
            form_data["postalcode"],
            current_date.strftime('%Y-%m-%d'),
            until_date.strftime('%Y-%m-%d'),
            form_data["membership_term"],
            0,
            form_data["card_number"],
            form_data["cvv"],
            form_data["card_expire"],
            form_data["card_holder_name"],
        ))
        form_data["memberid"] = g.db.lastrowid
        createPayment(form_data)
        activateMemebr(form_data)
        flash(f"""Congratulations! You have signed up and paid successfully. You can login with memberid {form_data["memberid"]} now.""")

def createPayment(form_data):
    sql_creat_payment = """
        INSERT INTO Payment 
        (Value,MemberID,ScheduleID,PaymentDate,PriceID)
        VALUES(%s,%s,%s,%s,%s)
    """
    g.db.execute(sql_creat_payment, (
            form_data["membership_price"],
            form_data["memberid"],
            None,
            datetime.today().strftime('%Y-%m-%d'),
            form_data["membership_price_id"]
        ))

def activateMemebr(form_data):
    sql = """UPDATE Member SET IsActive = 1 WHERE MemberID = %s"""
    g.db.execute(sql, (form_data["memberid"], ))