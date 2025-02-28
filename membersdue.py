from flask import Blueprint
from flask import render_template
from datetime import datetime
from auth import manager_required
from db import get_db



bp = Blueprint("membersdue", __name__, url_prefix="/membership/expiry")

now = datetime.now()
current_date = now.strftime("%Y-%m-%d")


@bp.route("/")
@manager_required # if this function need login first
def membersdue():
    db = get_db()
    db.execute("select memberid,FirstName, LastName, phonenumber, MembershipStartDate, MembershipEndDate, Term\
                from Member M join MembershipTerm t on M.Membershipterm=t.MembershiptermID\
                where MembershipEndDate<= ADDDATE(%s,30) and IsActive=1\
                order by MembershipEndDate",(current_date,))
              
    membershipinfo = db.fetchall()

    return render_template("manager/membersdue.html", membershipinfo = membershipinfo)