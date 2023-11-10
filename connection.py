from flask_mysqldb import MySQL


def db_connect(app):
    with app.app_context():
            db =MySQL(app)

            cursor = db.connection.cursor()

            print("Connection Server Information")
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("You are connected to - ", record, "\n")

            return cursor, db

