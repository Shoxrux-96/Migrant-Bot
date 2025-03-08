import sqlite3

# 📌 Ma'lumotlar bazasini yaratish
def create_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        full_name TEXT,
        gender TEXT,
        birth_date TEXT,
        passport TEXT,
        address TEXT,
        mahalla TEXT,
        location TEXT,
        purpose TEXT,
        job TEXT,
        salary TEXT,
        feedback TEXT,
        phone TEXT
    )
    """)
    conn.commit()
    conn.close()

# 📌 Foydalanuvchi ma'lumotlarini saqlash
def save_user(data):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO users (user_id, full_name, gender, birth_date, passport, address, mahalla, location, purpose, job, salary, feedback, phone)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

