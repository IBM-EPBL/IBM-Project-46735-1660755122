from flask import Blueprint, render_template

blue_print = Blueprint("print", __name__)

@blue_print.route('/')
def home():
    return render_template('index.html')