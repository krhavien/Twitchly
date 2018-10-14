import twitchly_db
from firebase_admin import db
import logging

database = twitchly_db.Database()

def all_user_ids():
    """Return a list of all user ids in the database."""
    ref = db.reference('users')
    snapshot = ref.get()
    return snapshot.keys() 

def refresh_all_user_info():
    """Refreshes the information of all people in the database."""
    user_ids = all_user_ids()
    for user_id in user_ids:
        database.get_info(user_id)
        logging.info("updated user id %s", user_id)



