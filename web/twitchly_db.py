import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import requests

import twitch_user 
import logging
logging.basicConfig(level=logging.INFO)

import random
random.seed(24601)

class Database:
    """
    Database to store information on Twitch users.

    Requires firebase-credentials.json for permissions.

    > database = Database()
    > database.get_info(19571641)
    {'mature': False, 'status': 'Doritos Bowl...', 'broadcaster_language': 'en', 'broadcaster_software': 'unknown_rtmp', 'display_name': 'Ninja', 'game': 'Call of Duty: Black Ops 4', 'language': 'en', 'id': '19571641', 'name': 'ninja', 'created_at': '2011-01-16 04:31:20', 'updated_at': '2018-10-13 21:24:41', 'partner': True, 'logo': 'https://static-cdn.jtvnw.net/jtv_user_pictures/cef31105-8a6e-4211-a74b-2f0bbd9791fb-profile_image-300x300.png', 'video_banner': 'https://static-cdn.jtvnw.net/jtv_user_pictures/8f5af87e-2062-46f8-9e74-ab20d0c2215e-channel_offline_image-1920x1080.png', 'profile_banner': 'https://static-cdn.jtvnw.net/jtv_user_pictures/3a3a6569-292f-489e-9046-3245a28be5c4-profile_banner-480.png', 'profile_banner_background_color': None, 'url': 'https://www.twitch.tv/ninja', 'views': 346534143, 'followers': 11747940, 'broadcaster_type': 'partner', 'description': 'Professional Battle Royale...', 'private_video': False, 'privacy_options_enabled': False, 'type': 'user', 'bio': 'Professional Battle Royale...'}
    """

    def __init__(self):
        cred = credentials.Certificate('firebase-credentials.json')
        default_app = firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://twitchly-datax.firebaseio.com/'
        })

    def get_user_info(self, id, force_online=False):
        """
        Get info about a user with ID.

        Attempts to retrieve info from database first. If no info is found,
        retrieves info from Twitch API directly.

        If no such ID exists, returns None.

        force_online(bool): if True, will update the database with the online information
        """
        if not force_online:
            stored_value = db.reference('users/' + str(id)).get()
            if stored_value:
                return stored_value

        retrieved_value = self.get_user_info_online(id)

        if not retrieved_value:
            return None

        self.set_user(id, retrieved_value)
        return retrieved_value

    def set_user(self, id, payload):
        """ Set a user with ID's information in the database to PAYLOAD."""
        return db.reference('users/' + str(id)).set(payload)

    def get_user_info_online(self, id):
        """
        Get info about a user with ID directly from Twitch API.
        
        Aggregates the information about ID as a user and channel.

        If no such user exists, returns None
        """

        try:
            user = twitch_user.client.users.get_by_id(id)
            channel = twitch_user.client.channels.get_by_id(id)
        except requests.exceptions.HTTPError:
            info.warning("Failed to retrieve information for %s", id)
            # If the user does not exist, return None
            return None

        # Ensure channel is JSON serializable by removing datetime objects
        channel["created_at"] = str(channel["created_at"])
        channel["updated_at"] = str(channel["updated_at"])

        combined = dict(channel)

        # I suspect that the only attributes are in user but not channel are
        # "type" and "bio", but I have a small sample size. user bio may be 
        # a duplicate of channel description.
        for attribute in user:
            if attribute not in combined:
                combined[attribute] = user[attribute]

        # Add who the user follows
        follows_ids = [c['id'] for c in twitch_user.get_all_follows(id)]
        combined["follows"] = follows_ids
        combined["num_follows"] = len(follows_ids)

        return combined

    def all_user_ids(self):
        """Return a list of all user ids in the database."""
        ref = db.reference('users')
        snapshot = ref.get()
        return snapshot.keys() 

    def refresh_all_user_info(self):
        """Refreshes the information of all people in the database."""
        user_ids = self.all_user_ids()
        for user_id in user_ids:
            self.get_user_info(user_id, force_online=True)
            logging.info("updated user id %s", user_id)


    def sample_ids(self, num_users, num_follows):
        """Return a random sample of unique user ids.

        Take NUM_FOLLOWS random follows from NUM_USERS random users.

        NUM_USERS must be less than the number of users in the database.
        Returns a set of at most NUM_USERS * NUM_FOLLOWS ids.
        """
        result = set()
        sample_of_users = random.sample(self.all_user_ids(), num_users)
        for user in sample_of_users:
            user_info = self.get_user_info(user)

            follows = user_info.get('follows')
            if not follows:
                continue

            sample_of_follows_per_user = random.sample(
                user_info['follows'], 
                min(num_follows, user_info['num_follows']),
            )
            for follow in sample_of_follows_per_user:
                result.add(follow)
        return result
