import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def setup_database():
    database = "users.db"

    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    name text NOT NULL,
                                    otp text NOT NULL,
                                    vector text NOT NULL
                                ); """

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_users_table)
    else:
        print("Error! cannot create the database connection.")
        
def add_user(name, otp, vector):
    conn = create_connection("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, otp, vector) VALUES (?, ?, ?)", (name, otp, vector))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
