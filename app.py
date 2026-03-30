from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2
from dbconfig import db_config

app = Flask(__name__)
app.secret_key = 'auditing_secret_key'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        cur.execute("""
            SELECT id, username, supplier_id
            FROM supplieraudit.users
            WHERE username = %s AND password = %s
        """, (username, password))

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['supplier_id'] = user[2]

            if user[2] is None:
                return redirect(url_for('internal_home'))
            else:
                return redirect(url_for('supplier_home'))

        else:
            return "Invalid credentials", 401

    return render_template('login.html')


@app.route('/internal')
def internal_home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('supplier_id') is not None:
        return "Unauthorized", 403

    return render_template('auditorhome.html')



@app.route('/supplier')
def supplier_home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    supplier_id = session.get('supplier_id')
    if supplier_id is None:
        return "Unauthorized", 403

    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    cur.execute("""
        SELECT name, address, city, state, country, zip
        FROM supplieraudit.supplier
        WHERE supplier_id = %s
    """, (supplier_id,))
    supplier = cur.fetchone()

    #TODO Make supplier object
    supplier_data = {
        "name": supplier[0],
        "address": supplier[1],
        "city": supplier[2],
        "state": supplier[3],
        "country": supplier[4],
        "zip": supplier[5],
    }

    cur.execute("""
        SELECT audit_id, total_score, draft, created_ts, last_edited_ts
        FROM supplieraudit.audit
        WHERE supplier_id = %s
        ORDER BY created_ts DESC
    """, (supplier_id,))
    audits = cur.fetchall()

    audit_list = []
    for a in audits:
        audit_list.append({
            "audit_id": a[0],
            "total_score": a[1],
            "draft": a[2],
            "created_ts": a[3],
            "last_edited_ts": a[4],
        })

    cur.close()
    conn.close()

    return render_template(
        'supplier.html',
        supplier=supplier_data,
        audits=audit_list
    )

@app.route('/listsuppliers')
def list_suppliers():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('supplier_id') is not None:
        return "Unauthorized", 403

    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    cur.execute("""
        SELECT supplier_id, name, address, city, state, country
        FROM supplieraudit.supplier
        ORDER BY name
    """)
    suppliers_data = cur.fetchall()
    cur.close()
    conn.close()

    #TODO make a supplier object
    suppliers_list = []
    for s in suppliers_data:
        suppliers_list.append({
            "id": s[0],
            "name": s[1],
            "address": s[2],
            "city": s[3],
            "state": s[4],
            "country": s[5]
        })

    return render_template('listsuppliers.html', suppliers=suppliers_list)

@app.route('/addsupplier', methods=['GET', 'POST'])
def add_supplier():
    if 'user_id' not in session or session.get('supplier_id') is not None:
        return "Unauthorized", 403

    if request.method == 'POST':
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        address = request.form.get('address', '')
        zip_code = request.form.get('zip', '')
        created_by = session['user_id']

        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO supplieraudit.supplier (name, address, city, state, country, zip, created_ts, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s)
        """, (name, address, city, state, country, zip_code, created_by))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('list_suppliers'))

    return render_template('addsupplier.html')

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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)