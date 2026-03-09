import psycopg2

from flask import Flask, render_template, jsonify
from dbconfig import db_config

app = Flask(__name__)


@app.route("/")
def hello():
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    cur.execute("SELECT CURRENT_TIMESTAMP;")
    date = cur.fetchone()[0]

    cur.close()
    conn.close()
    return render_template('helloworld.html', thedate=date)

@app.route('/test_db')
def test_db():
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"success": True, "PostgresSQL Version": db_version})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)