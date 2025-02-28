from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from datetime import date, datetime

from auth import trainer_required
from db import get_db

bp = Blueprint("trainermgmt", __name__, url_prefix="/trainer/management")


def serialize_members(members: list, many: bool = True) -> list:
    """ Serialize all members' data from database"""
    def func(member):
        return {
            'ID': member[0],
            'Firstname': member[1],
            'Lastname': member[2],
            'Fullname': f'{member[1]} {member[2]}',
            'Gender': member[3],
            'DayOfBirth': member[4].strftime('%Y-%m-%d'),
            'Email': member[5],
            'PhoneNumber': member[6],
            'Address': f'No.{member[8]}, {member[9]}, {member[10]}, {member[11]} {member[12]}',
            'HealthCondition': member[7],
            'MembershipStartDate': member[13],
            'MembershipEndDate': member[14],
            'MembershipType': member[22],
            'IsActive': member[16],
            'expired': member[14] < date.today()
        }

    memberlist = []
    for member in members:
        memberlist.append(func(member))
    return memberlist if many else memberlist[0]


@bp.route("/memberlist")
@trainer_required # this function need login first
def memberlist():
    """Show all the member."""
    db = get_db()
    db.execute(
        '''SELECT *
            FROM Member m
            JOIN MembershipTerm mt ON m.MembershipTerm = mt.MembershipTermID order by MemberID''')
    members = db.fetchall()
    member_list = serialize_members(members)
    return render_template("trainer/memberlist.html", member_list = member_list)

@bp.route("/memberlist/search", methods = ["GET", "POST"])
@trainer_required # this function need login first
def search():
    """Search member by name or ID."""
    db = get_db()
    search_type = request.form.get('search_type')
    db.execute('''
               SELECT * 
               FROM Member m
               JOIN MembershipTerm mt ON m.MembershipTerm = mt.MembershipTermID
               WHERE MemberID LIKE %s 
                OR Firstname LIKE %s 
                OR Lastname LIKE %s'''
                , (f'%{search_type}%', f'%{search_type}%', f'%{search_type}%'))
    members = db.fetchall()
    member_list = serialize_members(members)
    return render_template("trainer/memberlist.html", member_list = member_list)