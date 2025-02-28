from flask import Blueprint, g
from time import sleep
import datetime
from app import create_app
from db import get_db
from apscheduler.schedulers.background import BackgroundScheduler

bp = Blueprint("autopay", __name__)

# Creates a default Background Scheduler
sched = BackgroundScheduler()

def execute_autopay():
    with create_app().app_context():
        # fetch all membership information that expires on today
        today = datetime.date.today()
        today_str = today.strftime('%Y-%m-%d')
        db = get_db()
        query = '''
            SELECT 
                m.MemberID,
                m.Firstname,
                m.Lastname,
                m.CardNumber,
                m.NameOnCard,
                mt.Term AS "Membership Type",
                p.Value AS "Membership Fee",
                p.PriceID,
                m.MembershipEndDate
            FROM Member m
            JOIN MembershipTerm mt ON m.MembershipTerm = mt.MembershipTermID
            JOIN Price p USING (PriceID)
            WHERE MembershipEndDate = %s 
                AND m.IsActive = 1'''
        parameters = (today_str, )
        db.execute(query, parameters)
        results = db.fetchall()
        # deducting the next installment of membership fee from each members' bound bank cards
        for member_info in results:
            member_id = member_info[0]
            fee = member_info[6]
            price_id = member_info[7]
            membership_end_date = member_info[8]
            membership_type = member_info[5]
            # insert the payment information into database
            query1 = '''
                INSERT INTO Payment (Value, MemberID, PaymentDate, PriceID)
                VALUES (%s, %s, %s, %s)'''
            parameters = (fee, member_id, today_str, price_id)
            g.db.execute(query1, parameters)
            
            # update the membership start and end date
            if membership_type == "Monthly":
                query2 = '''
                    UPDATE Member
                    SET MembershipEndDate = DATE_ADD(%s, INTERVAL 1 MONTH)
                    WHERE MemberID = %s'''
                parameters = (membership_end_date, member_id)
                g.db.execute(query2, parameters)
                
                query = '''
                    UPDATE Member
                    SET MembershipStartDate = %s
                    WHERE MemberID = %s'''
                parameters = (today_str, member_id)
                g.db.execute(query, parameters)
            elif membership_type == "Yearly":
                query3 = '''
                    UPDATE Member
                    SET MembershipEndDate = DATE_ADD(%s, INTERVAL 1 YEAR)
                    WHERE MemberID = %s'''
                parameters = (membership_end_date, member_id)
                g.db.execute(query3, parameters)
                
                query = '''
                    UPDATE Member
                    SET MembershipStartDate = %s
                    WHERE MemberID = %s'''
                parameters = (today_str, member_id)
                g.db.execute(query, parameters)
            
    print(f"Executed payment function at {datetime.datetime.now()}")

# autopay at 1 am every day if needed
sched.add_job(execute_autopay, 'cron', hour=1, minute=0)
sched.start()

