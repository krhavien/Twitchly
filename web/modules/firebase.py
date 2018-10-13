import firebase_admin
import requests
from firebase_admin import credentials
from firebase_admin import db
import twitch_user

class Database:
    def __init__(self):
        cred = credentials.Certificate('firebase-credentials.json')
        default_app = firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://twitchly-datax.firebaseio.com/'
        })

    def get_info(self, id):
        """
        Get info about a person with ID.

        Attempts to retrieve info from database first. If not info is found,
        retrieves info from Twitch API directly.

        If no such ID exists, returns None.
        """
        stored_value = db.reference('users/' + str(id)).get()
        if stored_value:
            return stored_value

        retrieved_value = self.get_info(id)

        if not retrieved_value:
            return None

        self.set_user(id, retrieved_value)
        return retrieved_value

    def set_user(self, id, payload):
        """ Set a person with ID's information in the database to PAYLOAD."""
        return db.reference('users/' + str(id)).set(payload)

    def get_info_online(self, id):
        """
        Get info about a person with ID directly from Twitch API.
        
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
        # "type" and "bio", but I have a small sample size.
        for attribute in user:
            if attribute not in combined:
                combined[attribute] = user[attribute]
                print("added", attribute, user[attribute])

        return combined
