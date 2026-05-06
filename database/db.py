import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'spendly.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as count FROM users')
    if cursor.fetchone()['count'] > 0:
        conn.close()
        return

    password_hash = generate_password_hash('demo123')
    cursor.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
        ('Demo User', 'demo@spendly.com', password_hash)
    )
    user_id = cursor.lastrowid

    expenses = [
        (user_id, 25.50, 'Food', '2026-05-01', 'Grocery shopping'),
        (user_id, 45.00, 'Transport', '2026-05-02', 'Gas refill'),
        (user_id, 120.00, 'Bills', '2026-05-03', 'Electricity bill'),
        (user_id, 80.00, 'Health', '2026-05-05', 'Pharmacy'),
        (user_id, 60.00, 'Entertainment', '2026-05-08', 'Movie tickets'),
        (user_id, 150.00, 'Shopping', '2026-05-10', 'New clothes'),
        (user_id, 35.00, 'Food', '2026-05-12', 'Dinner out'),
        (user_id, 50.00, 'Other', '2026-05-15', 'Miscellaneous'),
    ]

    cursor.executemany(
        'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
        expenses
    )

    conn.commit()
    conn.close()