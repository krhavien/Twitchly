import logging
import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory)

application = Flask(__name__, static_folder='static')

@application.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@application.route('/')
@application.route('/index.html')
def send_index():
    return render_template('index.html')

@application.route('/about.html')
@application.route('/about')
def send_about():
    return render_template('about.html')

@application.route('/user.html')
@application.route('/user')
def send_user():
    username = request.args.get("username")
    if username:
        return render_template('user-profile.html', username=username)

    return render_template('user-search.html')

@application.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    application.run()

