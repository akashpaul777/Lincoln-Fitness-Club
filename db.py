import mysql.connector
from mysql.connector import FieldType
import click
from flask import current_app
from flask import g

dbconn = None
connection = None


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    # if "db" not in g:
    global dbconn
    global connection
    if connection is None or (
        connection is not None and connection.is_connected() == 0
    ):
        connection = mysql.connector.connect(
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASS"],
            host=current_app.config["DB_HOST"],
            database=current_app.config["DB_NAME"],
            autocommit=True,
        )
        dbconn = connection.cursor()
        # dbconn.execute("SET time_zone = 'Pacific/Auckland';")
    g.connection = connection
    g.db = dbconn
    g.db.row_factory = connection.cursor(dictionary=True)
    return g.db
