from flask import Flask
from flask import session
from flask import render_template
from werkzeug.exceptions import HTTPException
import base64


def base64_decode(value):
    try:
        return base64.b64decode(value).decode("utf-8")
    except Exception:
        return value


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_pyfile("config.py", silent=True)
    import db

    # Error page

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the exception
        app.logger.error(e)

        # Get the error code, name, and description
        error_code = 500
        error_name = "Internal Server Error"
        error_description = "An unexpected error occurred."

        if isinstance(e, HTTPException):
            error_code = e.code
            error_name = e.name
            error_description = e.description

        # Render the error template
        return (
            render_template(
                "error.html",
                error_code=error_code,
                error_name=error_name,
                error_description=error_description,
            ),
            error_code,
        )

    # Home page
    @app.route("/")
    def home():
        import db

        db = db.get_db()
        db.execute("SELECT * FROM News order by UpdateDate DESC;")
        allnews = db.fetchall()
        user_id = session.get("user_id")
        if user_id:
            db.execute(
                """SELECT s.StartDate, 
                        s.StartTime,
                        s.EndTime, 
                        s.Room, 
                        t.TrainingName
                        FROM Booking b 
                        inner join Schedule s on s.ScheduleID = b.ScheduleID 
                        inner join Training t on t.TrainingID = s.TrainingID
                        WHERE b.MemberID = %s AND s.StartDate > CURDATE()
                        order by TIMESTAMP(s.StartDate, s.StartTime) LIMIT 3;""",
                (user_id,),
            )
        upcoming_booking = db.fetchall()
        upcoming_booking_cols = [desc[0] for desc in db.description]
        # upcoming_booking = []
        # upcoming_booking_cols = []
        return render_template(
            "base.html",
            allnews=allnews,
            upcoming_booking=upcoming_booking,
            upcoming_booking_cols=upcoming_booking_cols,
        )

    # # auto membership fee paying
    # @app.before_first_request
    # def autopay():
    #     execute_autopay()

    # apply the blueprints to the app

    import auth
    import membermgmt
    import signup
    import staffprofile
    import trainingmgmt
    import memberprofile
    import bookclass
    import trainer_mgmt
    import manager_admin
    import groupclassmgmt
    import finance
    import userreport
    import memberattend
    import news
    import autopay
    import membersdue
    import popularclasses

    app.register_blueprint(auth.bp)
    app.register_blueprint(signup.bp)
    app.register_blueprint(staffprofile.bp)
    app.register_blueprint(trainingmgmt.bp)
    app.register_blueprint(memberprofile.bp)
    app.register_blueprint(bookclass.bp)
    app.register_blueprint(membermgmt.bp)
    app.register_blueprint(trainer_mgmt.bp)
    app.register_blueprint(manager_admin.bp)
    app.register_blueprint(groupclassmgmt.bp)
    app.register_blueprint(finance.bp)
    app.register_blueprint(userreport.bp)
    app.register_blueprint(memberattend.bp)
    app.register_blueprint(news.bp)
    app.register_blueprint(autopay.bp)
    app.register_blueprint(membersdue.bp)

    app.register_blueprint(popularclasses.bp)

    app.add_url_rule("/", endpoint="index")

    return app
