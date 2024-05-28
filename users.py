"""
* users.py
* 
* Copyright 2024, Filippini Giovanni
* 
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*         https://www.apache.org/licenses/LICENSE-2.0.txt
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
"""

from flask import abort, make_response, request
import sqlite3
from database import create_connection

DATABASE = "users.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def read_all():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return [dict(row) for row in users]

def create():
    user = request.get_json()
    name = user.get('name')
    otp = user.get('otp')
    vector = user.get('vector')
    
    if not name or not otp or not vector:
        abort(400, 'Invalid input')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO users (name, otp, vector) VALUES (?, ?, ?)', (name, otp, vector))
    conn.commit()
    user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    
    return {"id": user_id, "name": name, "otp": otp, "vector": vector}, 201

def read_one(userId):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (userId,)).fetchone()
    conn.close()
    
    if user is None:
        abort(404, f"User with id {userId} not found")
    
    return dict(user)

def update(userId):
    user = request.get_json()
    name = user.get('name')
    otp = user.get('otp')
    vector = user.get('vector')
    
    conn = get_db_connection()
    existing_user = conn.execute('SELECT * FROM users WHERE id = ?', (userId,)).fetchone()
    
    if existing_user is None:
        conn.close()
        abort(404, f"User with id {userId} not found")
    
    conn.execute('UPDATE users SET name = ?, otp = ?, vector = ? WHERE id = ?', (name, otp, vector, userId))
    conn.commit()
    conn.close()
    
    return {"id": userId, "name": name, "otp": otp, "vector": vector}

def delete(userId):
    conn = get_db_connection()
    existing_user = conn.execute('SELECT * FROM users WHERE id = ?', (userId,)).fetchone()
    
    if existing_user is None:
        conn.close()
        abort(404, f"User with id {userId} not found")
    
    conn.execute('DELETE FROM users WHERE id = ?', (userId,))
    conn.commit()
    conn.close()
    
    return make_response(f"User with id {userId} successfully deleted", 200)
