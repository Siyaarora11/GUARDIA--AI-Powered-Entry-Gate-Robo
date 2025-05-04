# modules/utils.py

import numpy as np
from config import DATABASE
import mysql.connector

def init_database():
    conn = mysql.connector.connect(**DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            mobile VARCHAR(255) NOT NULL,
            face_encoding BLOB NOT NULL,
            image BLOB
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            entry_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            access_key VARCHAR(255),
            image BLOB,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS super_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()
    

def add_user(name, mobile, face_encoding, image=None):
    conn = mysql.connector.connect(**DATABASE)
    cursor = conn.cursor()
    face_encoding_blob = face_encoding.tobytes()
    cursor.execute('''
        INSERT INTO users (name, mobile, face_encoding, image)
        VALUES (%s, %s, %s, %s)
    ''', (name, mobile, face_encoding_blob, image))
    conn.commit()
    cursor.close()
    conn.close()

def add_user_entry_log(name, access_key, image=None):
    conn = mysql.connector.connect(**DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE name = %s', (name,))
    user_id = cursor.fetchone()[0]
    cursor.execute('''
        INSERT INTO entries (user_id, entry_time, access_key, image)
        VALUES (%s, NOW(), %s, %s)
    ''', (user_id, access_key, image))
    conn.commit()
    cursor.close()
    conn.close()

def get_user_entry_log(user_id):
    conn = mysql.connector.connect(**DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT users.name, entries.entry_time, entries.access_key
        FROM entries
        JOIN users ON entries.user_id = users.id
        WHERE users.id = %s AND DATE(entries.entry_time) = CURDATE()
    ''', (user_id,))
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    return logs[0] if logs else None

def get_known_faces():
    conn = mysql.connector.connect(**DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT name, face_encoding, id FROM users')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    names = []
    encodings = []
    ids = []
    for row in rows:
        names.append(row[0])
        encodings.append(np.frombuffer(row[1], dtype=np.float64))
        ids.append(row[2])
    return names, encodings, ids

def create_super_user(email, password):
    from werkzeug.security import generate_password_hash
    conn = mysql.connector.connect(**DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM super_users')
    if cursor.fetchone()[0] > 0:
        cursor.close()
        conn.close()
        return "Error: A super user already exists."
    cursor.execute('''
        INSERT INTO super_users (email, password)
        VALUES (%s, %s)
    ''', (email, generate_password_hash(password)))
    conn.commit()
    cursor.close()
    conn.close()
    return "Super user created successfully."

def update_super_user(email, password):
    from werkzeug.security import generate_password_hash
    conn = mysql.connector.connect(**DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM super_users')
    if cursor.fetchone()[0] == 0:
        cursor.close()
        conn.close()
        return "Error: No super user exists to update."
    cursor.execute('''
        UPDATE super_users
        SET email = %s, password = %s
        WHERE id = (SELECT id FROM super_users LIMIT 1)
    ''', (email, generate_password_hash(password)))
    conn.commit()
    cursor.close()
    conn.close()
    return "Super user updated successfully."

def generate_random_access_key():
    from random import randint
    key = [str(randint(1, 9)) for _ in range(3)]
    return ' '.join(key)
