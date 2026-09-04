from flask import Blueprint, render_template

pages = Blueprint("pages", __name__)


@pages.route("/")
def home():
    return render_template("index.html")


@pages.route("/authors")
def authors_page():
    return render_template("authors.html")


@pages.route("/books")
def books_page():
    return render_template("books.html")