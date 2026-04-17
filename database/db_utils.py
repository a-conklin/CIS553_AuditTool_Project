import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="mydb",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )

def user_exists(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (username,))
    result = cur.fetchone()
    conn.close()
    return result is not None