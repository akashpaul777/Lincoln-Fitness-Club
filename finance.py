from flask import Blueprint
from flask import render_template
from flask import request
from auth import  manager_required
from db import get_db

bp = Blueprint("finance", __name__, url_prefix="/manager/finance")

@bp.route("/")
@manager_required # if this function need manager login first
def index():
    startdate = request.args.get('date1')
    enddate = request.args.get('date2')
    db = get_db()
    if startdate:
        db.execute("""SELECT 
                        CASE 
                            WHEN pr.IsMembershipTerm  = 1 THEN 'Subscription' 
                            ELSE 'PT Session' 
                            END AS Payment_Type,
                        SUM(p.Value) 
                        FROM Payment p join Price pr using(PriceID) 
                        where PaymentDate >= %s AND PaymentDate <= %s
                        GROUP BY pr.IsMembershipTerm ORDER BY pr.IsMembershipTerm;""",(startdate,enddate,))
    else:
        db.execute("""SELECT 
                        CASE 
                            WHEN pr.IsMembershipTerm  = 1 THEN 'Subscription' 
                            ELSE 'PT Session' 
                            END AS Payment_Type,
                        SUM(p.Value) 
                        FROM Payment p join Price pr using(PriceID) 
                        GROUP BY pr.IsMembershipTerm ORDER BY pr.IsMembershipTerm;""")
    financedata = db.fetchall()
    return render_template("manager/finance_rpt.html", financedata = financedata, startdate = startdate, enddate = enddate)
