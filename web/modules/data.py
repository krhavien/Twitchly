import sqlite3
import twitch_user

class Database:
    def __init__(self, database_file_name):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def insert_play(self, userId, game):
        raise NotImplementedError

    def insert_follow(self, userId, channelId):
        raise NotImplementedError

    def query(self, query_statement):
        raise NotImplementedError

class SqliteDatabase(Database):
    def __init__(self, database_file_name):
        self.conn = sqlite3.connect(database_file_name)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS FOLLOWS 
                (
                USER_ID     TEXT    NOT NULL,
                CHANNEL_ID  TEXT    NOT NULL 
                );''')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS USERNAME
                (
                USER_ID  TEXT    NOT NULL,
                USERNAME        TEXT    NOT NULL
                );''')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS PLAYS
                (
                CHANNEL_ID  TEXT    NOT NULL,
                GAME        TEXT    NOT NULL
                );''')
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def insert_play(self, userId, game):
        self.conn.execute('''
            INSERT INTO PLAYS 
            (CHANNEL_ID, GAME)
            VALUES
            ('%s', '%s');
        ''' % (userId, game))
        self.conn.commit()

    def insert_follow(self, userId, channelId):
        self.conn.execute('''
            INSERT INTO FOLLOWS 
            (USER_ID, CHANNEL_ID)
            VALUES
            ('%s', '%s');
        ''' % (userId, channelId))
        self.conn.commit()

    def query(self, query_statement):
        cursor = self.conn.cursor()
        cursor.execute(query_statement)
        return cursor.fetchall()


def add_user_follows(database, username):
    """Add USERNAME's follows to DATABASE."""
    user_id = twitch_user.get_user_id(username)
    follows = twitch_user.get_all_follows(user_id)
    num_inserted = 0
    for follow in follows:
        database.insert_follow(user_id, follow['id'])
        num_inserted += 1
    return num_inserted


if __name__ == "__main__":
    db = SqliteDatabase("twitch_api.db")
    print(add_user_follows(db, "Ninja"))
