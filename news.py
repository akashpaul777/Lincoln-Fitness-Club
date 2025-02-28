from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from auth import manager_required
from db import get_db

bp = Blueprint("news", __name__, url_prefix="/manager/news")

@bp.route("/")
@manager_required # if this function need manager login first
def listnews():
    """Show all the gym news."""
    db = get_db()
    db.execute("SELECT * FROM News order by NewsID DESC")
    news_list = db.fetchall()
    return render_template("/manager/news/news.html", news_list = news_list)

@bp.route("/add", methods=["GET","POST"])
@manager_required # if this function need manager login first
def addnews():
    if request.method == 'GET':
        return render_template("/manager/news/addnews.html")
    elif request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        db = get_db()
        db.execute("""INSERT INTO News (Title,Content,UpdateDate) VALUES ( %s,%s,NOW());""",(title,content,))
        flash('The new has been add!')
        return redirect("/manager/news")

@bp.route("/edit", methods=["POST"])
@manager_required # if this function need manager login first
def editnews():
    newsid = request.form.get('newsid')
    db = get_db()
    db.execute("SELECT * FROM News WHERE NewsID = %s;",(newsid,))
    news_list = db.fetchall()
    return render_template("/manager/news/editnews.html", news_list = news_list, newsid = newsid)

@bp.route("/update", methods=["POST"])
@manager_required # if this function need manager login first
def updatenews():
        newsid = request.form.get('newsid')
        title = request.form.get('title')
        content = request.form.get('content')
        db = get_db()
        db.execute("""UPDATE News SET Title = %s, Content = %s, 
                 UpdateDate = NOW() WHERE NewsID = %s;""",
                (title,content,newsid,))
        flash('The change has been saved!')
        return redirect("/manager/news")


@bp.route("/del", methods=["POST"])
@manager_required # if this function need manager login first
def delnews():
        newsid = request.form.get('newsid')
        db = get_db()
        db.execute("DELETE FROM News WHERE NewsID = %s;",(newsid,))
        flash('The news has been deleted!')
        return redirect("/manager/news")
