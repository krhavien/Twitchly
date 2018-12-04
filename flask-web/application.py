import logging
import os
import twitchly_db
import twitch_user
import random
from model import create_model

from flask import (Flask, redirect, render_template, request,
                   send_from_directory)

database = twitchly_db.Database()
application = Flask(__name__, static_folder='static')


@application.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)

@application.route('/fonts/<path:path>')
def send_fonts(path):
    return send_from_directory('static/fonts', path)

@application.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

@application.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('static/img', path)

@application.route('/')
@application.route('/index.html')
def send_index():
    return render_template('index.html')

@application.route('/about.html')
@application.route('/about')
def send_about():
    return render_template('about.html')

@application.route('/contact.html')
@application.route('/contact')
def send_contact():
    return render_template('contact.html')


@application.route('/user.html')
@application.route('/user')
def send_user():
    username = request.args.get("username")
    if username:
        if not username.isalnum():
            return render_template('user-search.html', error_msg="ERROR: username must be alphanumeric.")

        user_id = twitch_user.get_user_id(username)
        logger.info(user_id)
        if not user_id:
            return render_template('user-profile.html', username="User not found", userinfo="")

        user_info = database.get_user_info(user_id)
        try: 
            cluster_members, predicted_cluster, filters_used = rec_model.get_closest_matches(channel_id=user_id, db=database)
            nm = rec_model
            while len(cluster_members) == 0 and nm.n_clusters/2 > 0:
                n_clusters = nm.n_clusters
                nm = create_model(n_clusters=n_clusters/2)
                logger.info(nm.n_clusters)
                nm.train(assign_clusters=True)
                cluster_members, predicted_cluster, filters_used = nm.get_closest_matches(channel_id=user_id, db=database)
            
            name_index = 2
            num_names = 10
            num_top = 4
            num_new = num_names - num_top 
            lst_cluster_members = list(cluster_members['display_name'])
            # lst_cluster_members = [tuple(x) for x in cluster_members[['display_name', 'game', 'followers', 'broadcaster_language', 'views']]]
            cluster_member_names = random.sample(lst_cluster_members[:num_names], num_top) + [lst_cluster_members[num_names:][i] for i in sorted(random.sample(range(len(lst_cluster_members[num_names:num_names+1000])), num_new))]
            # random.shuffle(cluster_member_names)

            # log important values to console
            logger.info(cluster_member_names)
            logger.info(filters_used)
            logger.info(predicted_cluster)
        except Exception as e:
            logger.warn(e)
            cluster_member_names = []
        return render_template(
                'user-profile.html', 
                username=username,
                userinfo=user_info,
                cluster_member_names=cluster_member_names) 

    return render_template('user-search.html')

@application.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

if __name__ == "__main__":
    rec_model = create_model(n_clusters=10)
    print("model trained!")
    rec_model.train(assign_clusters=True)
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    application.run()

