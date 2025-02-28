from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from auth import login_required, staff_required
from db import get_db

bp = Blueprint("staffprofile", __name__, url_prefix="/staff/profile")

@bp.route("/")
@staff_required # if this function need trainer login first
def index():
    db = get_db()
    db.execute("SELECT * FROM Staff where StaffID = %s;",(g.user.id,))
    trainerinfo = db.fetchall()
    #print(staffinfo)
    return render_template("trainer/profile.html", trainerinfo = trainerinfo)

@bp.route("/update", methods=["POST"])
@staff_required # if this function need trainer login first
def updateProfile():
    staffid = request.form.get('staffid')
    email = request.form.get('email')
    phonenumber = request.form.get('Phonenumber')
    house = request.form.get('house')
    street = request.form.get('street')
    town = request.form.get('town')
    city = request.form.get('city')
    postalcode = request.form.get('postalcode')
    introduction = request.form.get('introduction')
    db = get_db()
    db.execute("""UPDATE Staff SET Email = %s, PhoneNumber = %s, 
                HouseNumberName = %s, Street = %s, Town = %s,
                City = %s, Postalcode = %s, Introduction = %s 
                WHERE StaffID = %s;""",
                (email,phonenumber,house,street,town,city,postalcode,introduction,staffid,))
    flash('The changes are already saved!')
    return redirect("/staff/profile")






