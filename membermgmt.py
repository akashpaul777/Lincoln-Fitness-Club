from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify
from werkzeug.datastructures import MultiDict
from datetime import date
from auth import manager_required
import json
from db import get_db
import base64
bp = Blueprint("management", __name__, url_prefix="/management")


def serialize_members(members: list, many: bool = True) -> list:
    """
    Serialize member data from database query result
    """

    def func(member):
        return {
            'id': member[0],
            'Fullname': f'{member[1]}·{member[2]}',
            'Firstname': member[1],
            'Lastname': member[2],
            'gender': member[3],
            'DayOfBirth': member[4].strftime('%Y-%m-%d'),
            'email': member[5],
            'PhoneNumber': member[6],
            'HealthCondition': member[7],
            'HouseNumberName': member[8],
            'Street': member[9],
            'Town': member[10],
            'City': member[11],
            'Postalcode': member[12],
            'address': f'No.{member[8]},{member[9]},{member[10]},{member[11]} {member[12]}',
            'MembershipStartDate': member[13],
            'MembershipEndDate': member[14],
            'IsActive': member[16],
            'cardNumber': member[17],
            'CVV': member[18],
            'CardExpiry': member[19],
            'NameOnCard': member[20],
            'MembershipTerm': member[15],
            'expired': member[14] < date.today()
        }

    member_list = []
    for member in members:
        member_list.append(func(member))
    return member_list if many else member_list[0]


@bp.route("/member/list", endpoint='member_list')
@manager_required  # need manager permission
def index():
    """Show all the member."""
    db = get_db()
    db.execute('SELECT * FROM Member;')
    members = db.fetchall()
    member_list = serialize_members(members)
    return render_template("manager/member/list.html", memberList=member_list)


@bp.route("/member/create", methods=("GET", "POST"), endpoint='member_create')
@manager_required  # need manager permission
def create():
    """Create a new member."""
    for key, value in request.form.items():
        if not value:
            return flash(f'{key} is required.')
    db = get_db()
    if request.method == "POST":
        form = MultiDict(request.form)
        form['HealthCondition'] = ', '.join(request.form.getlist('HealthCondition'))
        form['CardNumber'] = base64.b64encode(form['CardNumber'].encode('utf-8')).decode('utf-8')
        form['CVV'] = base64.b64encode(form['CVV'].encode('utf-8')).decode('utf-8')
        # form['CardExpiry'] = base64.b64encode(form['CardExpiry'].encode('utf-8')).decode('utf-8')
        form['NameOnCard'] = base64.b64encode(form['NameOnCard'].encode('utf-8')).decode('utf-8')
        field_names = ','.join(form.keys())
        insert_data = [(form.get(k)) for k in form.keys()]
        insert_sql = f"INSERT INTO Member ({field_names}) VALUES ({', '.join(['%s' for _ in form.keys()])})"
        conn = g.connection
        db.execute(insert_sql, insert_data)
        conn.commit()
        member_id = db.lastrowid
        query_price_sql = """
            SELECT Price.Value, Price.PriceID FROM Price
            JOIN MembershipTerm ON Price.PriceID = MembershipTerm.PriceID
            WHERE MembershipTerm.MembershipTermID = %s;

        """
        db.execute(query_price_sql, (request.form.get('MembershipTerm'),))
        price, priceid = db.fetchone()[:2]
        add_payment_sql = ("INSERT INTO Payment "
                           "(Value, MemberID, PaymentDate, PriceID) "
                           "VALUES (%s, %s, %s, %s)")
        db.execute(add_payment_sql, (price, member_id, date.today(), priceid))
        conn.commit()
        flash(f'Member has already been added!')
        return redirect(url_for("management.member_list"))
    db.execute("SELECT * FROM MembershipTerm")
    terms = db.fetchall()
    return render_template("manager/member/create.html", terms=terms)


@bp.route("member/update", methods=("GET", "POST"), endpoint='member_update')
@manager_required  # need manager permission
def update():
    """Update a exist member."""
    db = get_db()
    if request.method == 'GET':
        member_id = request.args.get('id')
        db.execute("SELECT * FROM Member WHERE MemberID = %s", (member_id,))
        member = db.fetchall()
        member_info = serialize_members(member, False)
        db.execute("SELECT * FROM MembershipTerm")
        terms = db.fetchall()
        return render_template("manager/member/update.html", member_info=member_info, terms=terms)
    else:
        member_id = request.form.get('id')
        form = MultiDict(request.form)
        form['CardNumber'] = base64.b64encode(form['CardNumber'].encode('utf-8')).decode('utf-8')
        form['CVV'] = base64.b64encode(form['CVV'].encode('utf-8')).decode('utf-8')
        # form['CardExpiry'] = base64.b64encode(form['CardExpiry'].encode('utf-8')).decode('utf-8')
        form['NameOnCard'] = base64.b64encode(form['NameOnCard'].encode('utf-8')).decode('utf-8')
        form['HealthCondition'] = ', '.join(request.form.getlist('HealthCondition'))
        member_info = [(k, v) for k, v in form.items() if k != 'id']
        update_sql = "UPDATE Member SET "
        update_sql += ", ".join([f"{k}=%s" for k, _ in member_info])
        update_sql += " WHERE MemberID=%s"
        conn = g.connection
        db.execute(update_sql, [v for _, v in member_info] + [member_id])
        conn.commit()
        flash(f'Member {request.form["id"]} Updated successfully')
        return redirect(url_for("management.member_list"))


@bp.route("/member/status", methods=("POST",), endpoint='inactive')
@manager_required  # need manager permission
def inactive():
    """Change member status.
    """
    data = json.loads(request.data)
    db = get_db()
    db.execute("UPDATE Member SET IsActive=%s WHERE MemberID = %s",
               (data['status'], data['id']))
    g.connection.commit()
    return jsonify({"code": 0, "msg": "Deactivate successfully"})


@bp.route("/member/search", methods=("POST",), endpoint='member_search')
@manager_required  # need manager permission
def serach():
    """ Search member by name or ID
    """
    db = get_db()
    searchKey = request.form.get('searchKey')
    inactive = request.form.get('inactive')
    if inactive == '1':
        db.execute("SELECT * FROM Member WHERE IsActive=0")
    else:
        db.execute("SELECT * FROM Member WHERE MemberID LIKE %s OR Firstname LIKE %s OR Lastname LIKE %s",
                   (f'%{searchKey}%', f'%{searchKey}%', f'%{searchKey}%'))
    members = db.fetchall()
    member_list = serialize_members(members)
    return render_template("manager/member/list.html", memberList=member_list, inactive=inactive)