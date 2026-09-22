import sqlite3

def init_db():
    conn = sqlite3.connect("study.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_data(question, answer):
    conn = sqlite3.connect("study.db")
    c = conn.cursor()
    c.execute("INSERT INTO history (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect("study.db")
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return data

def clear_history():
    conn = sqlite3.connect("study.db")
    c = conn.cursor()
    c.execute("DELETE FROM history")
    conn.commit()
    conn.close()

def create_user(username, password):
    conn = sqlite3.connect("study.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect("study.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user
