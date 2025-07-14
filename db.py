import sqlite3
from typing import List, Tuple
from datetime import datetime, timedelta

DB_PATH = "vpn_bot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        server_id TEXT,
        access_key_id TEXT,
        access_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )''')
    conn.commit()
    conn.close()

def add_user(user_id: int, username: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()
    conn.close()

def add_key(user_id: int, server_id: str, access_key_id: str, access_url: str, expires_at: str = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if not expires_at:
        expires_at = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO keys (user_id, server_id, access_key_id, access_url, expires_at) VALUES (?, ?, ?, ?, ?)',
              (user_id, server_id, access_key_id, access_url, expires_at))
    conn.commit()
    conn.close()

def get_keys(user_id: int) -> List[Tuple]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT server_id, access_key_id, access_url, created_at, expires_at FROM keys WHERE user_id = ?', (user_id,))
    keys = c.fetchall()
    conn.close()
    return keys

def get_expired_keys(now=None):
    import sqlite3
    from datetime import datetime
    if now is None:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, user_id, server_id, access_key_id, expires_at FROM keys WHERE expires_at IS NOT NULL AND expires_at <= ?', (now,))
    keys = c.fetchall()
    conn.close()
    return keys

def mark_key_deleted(key_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE keys SET expires_at = NULL WHERE id = ?', (key_id,))
    conn.commit()
    conn.close()

def delete_key(user_id: int, server_id: str, access_key_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM keys WHERE user_id = ? AND server_id = ? AND access_key_id = ?', 
              (user_id, server_id, access_key_id))
    conn.commit()
    conn.close() 