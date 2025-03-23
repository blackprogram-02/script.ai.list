import sqlite3
import os
from lib.log import log
import xbmc

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)  # Ensure the directory exists
        self.conn = sqlite3.connect(self.db_path)
        log(f"Database initialized at path: {self.db_path}", level=xbmc.LOGINFO)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS user_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS watch_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    added_at TEXT NOT NULL,
                    UNIQUE(item_id, item_type)
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    added_at TEXT NOT NULL,
                    UNIQUE(item_id, item_type)
                )
            ''')
        log("Database tables created or verified.", level=xbmc.LOGINFO)

    def insert_user_info(self, key, value):
        log("Inserting User Info.", level=xbmc.LOGINFO)
        with self.conn:
            self.conn.execute('''
                INSERT INTO user_info (key, value) VALUES (?, ?)
            ''', (key, value))
        log(f"Inserted user info: key={key}, value={value}", level=xbmc.LOGDEBUG)

    def get_user_info(self, key):
        log("Fetching user info.", level=xbmc.LOGINFO)
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT value FROM user_info WHERE key = ?
        ''', (key,))
        row = cursor.fetchone()
        log(f"Retrieved user info for key={key}: {row}", level=xbmc.LOGDEBUG)
        return row[0] if row else None

    def update_user_info(self, key, value):
        log("Update user info.", level=xbmc.LOGINFO)
        with self.conn:
            self.conn.execute('''
                UPDATE user_info SET value = ? WHERE key = ?
            ''', (value, key))
        log(f"Updated user info: key={key}, value={value}", level=xbmc.LOGDEBUG)

    def delete_user_info(self, key):
        log("Deleting user info.", level=xbmc.LOGINFO)
        with self.conn:
            self.conn.execute('''
                DELETE FROM user_info WHERE key = ?
            ''', (key,))
        log(f"Deleted user info for key={key}", level=xbmc.LOGDEBUG)

    def insert_watch_history(self, watch_history):
        with self.conn:
            for item in watch_history:
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM watch_history WHERE item_id = ? AND item_type = ?
                ''', (item[0], item[1]))
                if cursor.fetchone()[0] == 0:
                    self.conn.execute('''
                        INSERT INTO watch_history (item_id, item_type, title, added_at) VALUES (?, ?, ?, ?)
                    ''', item)
                    log(f"Inserted watch history item: {item}", level=xbmc.LOGDEBUG)
        log("Watch history updated.", level=xbmc.LOGINFO)

    def get_watch_history(self):
        log("Fetching Watch history.", level=xbmc.LOGINFO)
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT item_id, item_type, title, added_at FROM watch_history
        ''')
        rows = cursor.fetchall()
        log(f"Retrieved watch history: {rows}", level=xbmc.LOGDEBUG)
        return rows

    def get_latest_added_at(self):
        log("Fetching Last Watched Item.", level=xbmc.LOGINFO)
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT MAX(added_at) FROM watch_history
        ''')
        row = cursor.fetchone()
        log(f"Latest added_at from watch history: {row}", level=xbmc.LOGDEBUG)        
        return row[0] if row else None

    def insert_watchlist(self, watchlist):
        with self.conn:
            for item in watchlist:
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM watchlist WHERE item_id = ? AND item_type = ?
                ''', (item[0], item[1]))
                if cursor.fetchone()[0] == 0:
                    self.conn.execute('''
                        INSERT INTO watchlist (item_id, item_type, title, added_at) VALUES (?, ?, ?, ?)
                    ''', item)
                    log(f"Inserted watchlist item: {item}", level=xbmc.LOGDEBUG)
        log("Watchlist updated.", level=xbmc.LOGINFO)

    def get_watchlist(self):
        log("Fetching watchlist.", level=xbmc.LOGINFO)
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT item_id, item_type, title, added_at FROM watchlist
        ''')
        rows = cursor.fetchall()
        log(f"Retrieved watchlist: {rows}", level=xbmc.LOGDEBUG)
        return cursor.fetchall()

    def get_latest_added_at_watchlist(self):
        log("Fetching last added watchlist item.", level=xbmc.LOGINFO)
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT MAX(added_at) FROM watchlist
        ''')
        row = cursor.fetchone()
        log(f"Latest added_at from watchlist: {row}", level=xbmc.LOGDEBUG)
        return row[0] if row else None