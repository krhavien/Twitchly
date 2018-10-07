import pandas as pd
from twitch import TwitchClient

# Let's create the client by passing in your specific client id.
client = TwitchClient(client_id = "zjwe67emf2ri3ecyqvihgzhb1r3l4i")

def get_user_id(user_name: str):
    users = client.users.translate_usernames_to_ids([user_name])
    print("Branch demo")
    return users[0].id

def get_all_follows(user_id: str, show_progress=False):
    """Return a list of all channels a user follows"""
    channels = []

    # We want to avoid adding dupliciate users, which the API has retrieved in the past
    added_channel_names = set()
    offset = 0

    followed_channels = client.users.get_follows(user_id, limit=100)
    while followed_channels:
        for followed_channel in followed_channels:
            offset += 1
            channel = followed_channel.channel

            if channel.display_name not in added_channel_names:
                channels.append(followed_channel.channel)
                added_channel_names.add(channel.display_name)

        followed_channels = client.users.get_follows(user_id, limit=100, offset=offset)
        if show_progress:
            print(offset, end=' ')
    if show_progress:
        print("finished")
    return channels

def get_follow_game_distribution(user_id: str):
    """
    Return a mapping from game to proportion of follows.

    'Overcooked! 2' -> .05 means that 5% of the user's followed channels focus on 'Overcooked! 2'.
    """
    channels = get_all_follows(user_id, True)
    channel_df = pd.DataFrame.from_records(channels)
    return channel_df['game'].value_counts(normalize=True)
