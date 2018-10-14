import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import requests

import modules.twitch_user as twitch_user

class Database:
    """
    Database to store information on Twitch users.

    Requires firebase-credentials.json for permissions.

    > database = Database()
    > database.get_info(19571641)
    {'mature': False, 'status': 'Doritos Bowl...', 'broadcaster_language': 'en', 'broadcaster_software': 'unknown_rtmp', 'display_name': 'Ninja', 'game': 'Call of Duty: Black Ops 4', 'language': 'en', 'id': '19571641', 'name': 'ninja', 'created_at': '2011-01-16 04:31:20', 'updated_at': '2018-10-13 21:24:41', 'partner': True, 'logo': 'https://static-cdn.jtvnw.net/jtv_user_pictures/cef31105-8a6e-4211-a74b-2f0bbd9791fb-profile_image-300x300.png', 'video_banner': 'https://static-cdn.jtvnw.net/jtv_user_pictures/8f5af87e-2062-46f8-9e74-ab20d0c2215e-channel_offline_image-1920x1080.png', 'profile_banner': 'https://static-cdn.jtvnw.net/jtv_user_pictures/3a3a6569-292f-489e-9046-3245a28be5c4-profile_banner-480.png', 'profile_banner_background_color': None, 'url': 'https://www.twitch.tv/ninja', 'views': 346534143, 'followers': 11747940, 'broadcaster_type': 'partner', 'description': 'Professional Battle Royale...', 'private_video': False, 'privacy_options_enabled': False, 'type': 'user', 'bio': 'Professional Battle Royale...'}
    """

    def __init__(self):
        cred = credentials.Certificate('modules/firebase-credentials.json')
        default_app = firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://twitchly-datax.firebaseio.com/'
        })

    def get_user_info(self, id):
        """
        Get info about a user with ID.

        Attempts to retrieve info from database first. If no info is found,
        retrieves info from Twitch API directly.

        If no such ID exists, returns None.
        """
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

        return combined
