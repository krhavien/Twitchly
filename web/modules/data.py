import sqlite3
import twitch_user
import logging

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
                CHANNEL_ID  TEXT    NOT NULL,
                FOREIGN KEY (CHANNEL_ID) REFERENCES PLAYS(CHANNEL_ID),
                CONSTRAINT FOLLOWING UNIQUE (USER_ID, CHANNEL_ID)
                );''')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS NAME
                (
                USER_ID  TEXT    PRIMARY KEY,
                USERNAME TEXT    NOT NULL
                );''')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS PLAYS
                (
                CHANNEL_ID  TEXT    NOT NULL,
                GAME        TEXT    NOT NULL,
                CONSTRAINT CHANNEL_PLAYS UNIQUE (CHANNEL_ID, GAME)
                );''')

        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def insert_play(self, user_id, game_name):
        self.conn.execute('''
            INSERT INTO PLAYS 
            (CHANNEL_ID, GAME)
            VALUES
            ("%s", "%s");
        ''' % (user_id, game_name))
        self.conn.commit()

    def insert_follow(self, user_id, channel_id):
        self.conn.execute('''
            INSERT INTO FOLLOWS 
            (USER_ID, CHANNEL_ID)
            VALUES
            ('%s', '%s');
        ''' % (user_id, channel_id))
        self.conn.commit()

    def insert_name(self, user_id, username):
        self.conn.execute('''
            INSERT INTO NAME 
            (USER_ID, USERNAME)
            VALUES
            ('%s', '%s');
        ''' % (user_id, username))
        self.conn.commit()


    def query(self, query_statement):
        cursor = self.conn.cursor()
        cursor.execute(query_statement)
        return cursor.fetchall()

    def get_user_id(self, username):
        """Get the user id for USERNAME from DATABASE else Twitch API.

        Will abort addition database if user id is in DATABASE

        :returns: user id
        """
        query_result = self.query('SELECT USER_ID FROM NAME WHERE USERNAME == "%s";' % username)

        if query_result:
            logging.info("user id found in database")
            return query_result[0][0]

        user_id = twitch_user.get_user_id(username)
        self.insert_name(user_id, username)
        logging.info("stored user id for user %s" % username)
        return user_id


    def get_user_follow_info(self, username, force=False):
        """Retrieves USERNAME's follow info from DATABASE else Twitch API.
        
        Stores USERNAME's user id if not already in database.

        FORCE: whether to pull results from the API regardless of caching

        :returns: list of ids
        """
        user_id = self.get_user_id(username)

        query_result = self.query('SELECT CHANNEL_ID FROM FOLLOWS WHERE USER_ID == "%s";' % user_id)

        if query_result and not force:
            logging.info("user follows in database")
            return [channel[0] for channel in query_result]

        follows = twitch_user.get_all_follows(user_id)

        encountered_repeats = False
        for follow in follows:
            try:
                logging.info("%s %s", follow['id'], follow['game'])
                self.insert_play(follow['id'], follow['game'])
            except sqlite3.IntegrityError:
                encountered_repeats = True

            try:
                self.insert_follow(user_id, follow['id'])
            except sqlite3.IntegrityError:
                encountered_repeats = True


        if encountered_repeats:
            logging.info("encountered previously stored follows")

        return [follow['id'] for follow in follows]

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    db = SqliteDatabase("twitch_api.db")
    # print(add_user_follows(db, "Ninja"))
