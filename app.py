from flask import Flask

from errors import register_error_handlers

from routes.pages import pages
from routes.authors import authors_bp
from routes.books import books_bp
# from db import get_connection

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

app.register_blueprint(pages)
app.register_blueprint(authors_bp)
app.register_blueprint(books_bp)

#test if web server is ON
# @app.route("/hello")
# def hello():
#     return "Flask is working"

# sending JSON over HTTP
# @app.route("/hello")
# def hello():
#     return {"message": "Flask is working", "status": "ok"}

# #test DB connection
# @app.route("/db-test")
# def db_test():
#     connection = get_connection()
#     cursor = connection.cursor(dictionary=True, buffered=True)
#     cursor.execute("SELECT COUNT(*) FROM authors")
#     result = cursor.fetchone()
#     cursor.close()
#     connection.close()
#     return {"authors_in_database": result[0]}

register_error_handlers(app) 

if __name__ == "__main__":
    app.run(debug=True)