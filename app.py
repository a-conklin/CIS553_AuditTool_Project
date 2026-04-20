from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify
import psycopg2
from dbconfig import db_config
from service.action_item_service import ActionItemService
from service.audit_service import AuditService
from service.audit_template_service import AuditTemplateService
from service.supplier_service import SupplierService

app = Flask(__name__)
app.secret_key = 'auditing_secret_key'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        cur.execute("""
            SELECT id, username, supplier_id, email
            FROM supplieraudit.users
            WHERE email = %s AND password = %s
        """, (email, password))

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['supplier_id'] = user[2]
            session['email'] = user[3]

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

    supplier_data = SupplierService.get_supplier_by_id(supplier_id)
    audit_list = AuditService.get_audits_for_supplier(supplier_id)

    for audit in audit_list:
        audit.action_items_pending = ActionItemService.get_action_item_count_for_audit(audit.audit_id)

    return render_template(
        'supplierhome.html',
        supplier=supplier_data,
        audits=audit_list
    )

@app.route('/listsuppliers')
def list_suppliers():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('supplier_id') is not None:
        return "Unauthorized", 403

    suppliers_list = SupplierService.get_all_suppliers()
    supplier_scores = SupplierService.get_latest_audit_scores_by_supplier()

    return render_template(
        'listsuppliers.html',
        suppliers=suppliers_list,
        supplier_scores=supplier_scores
    )

@app.route('/addsupplier', methods=['GET', 'POST'])
def add_supplier():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get('supplier_id') is not None:
        return "Unauthorized", 403

    if request.method == 'POST':
        data = {
            "name": request.form['name'],
            "city": request.form['city'],
            "state": request.form['state'],
            "country": request.form['country'],
            "address": request.form.get('address', ''),
            "zip": request.form.get('zip', '')
        }

        result = SupplierService.create_supplier(data, session['user_id'])

        if result["status"] == "success":
            return redirect(url_for('list_suppliers'))
        else:
            return result["message"], 500

    return render_template('addsupplier.html')

@app.route('/list_templates')
def list_templates():

    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get('supplier_id') is not None:
        return "Unauthorized", 403

    templates = AuditTemplateService.get_templates()

    return render_template('template_list.html', templates=templates)

@app.route('/template_builder', methods=['GET', 'POST'])
def template_builder():

    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get('supplier_id') is not None:
        return "Unauthorized", 403

    if request.method == 'POST':
        data = request.get_json()
        user_id = session['user_id']

        result = AuditTemplateService.create_template(data, user_id)
        return jsonify(result)

    return render_template('template_builder.html')

@app.route("/template_viewer/<int:template_id>")
def view_template(template_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get('supplier_id') is not None:
        return "Unauthorized", 403
    template = AuditTemplateService.get_template_by_id(template_id)  # returns entity with groups & questions
    return render_template("template_viewer.html", template=template)

@app.route("/start_audit", methods=["GET", "POST"])
def start_audit():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get('supplier_id') is not None:
        return "Unauthorized", 403

    user_id = session["user_id"]

    # Prepopulate supplier if ?supplier_id=xxx is passed in the URL
    preselected_supplier_id = request.args.get("supplier_id", type=int)

    if request.method == "POST":
        supplier_id = int(request.form["supplier_id"])
        template_id = int(request.form["template_id"])

        # Create a new draft audit
        audit_id = AuditService.create_draft_audit(user_id, supplier_id, template_id)

        return redirect(url_for("edit_audit", audit_id=audit_id))

    # GET request
    if preselected_supplier_id:
        supplier = SupplierService.get_supplier_by_id(preselected_supplier_id)
        suppliers = [supplier] if supplier else []
    else:
        suppliers = SupplierService.get_all_suppliers()

    templates = AuditTemplateService.get_templates()

    return render_template(
        "start_audit.html",
        suppliers=suppliers,
        preselected_supplier_id=preselected_supplier_id,
        templates=templates
    )

@app.route("/edit_audit/<int:audit_id>", methods=["GET", "POST"])
def edit_audit(audit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get('supplier_id') is not None:
        return "Unauthorized", 403

    user_id = session["user_id"]

    # Load audit and template
    audit, template, findings_by_question, supplier_name, auditor_name, action_items = AuditService.get_audit_with_findings(audit_id)

    if not audit:
        return "Audit not found", 404

    # Prevent editing if final
    if audit.draft == 'N':
        return render_template(
            "view_audit.html",  # read-only page
            audit=audit,
            template=template,
            findings_by_question=findings_by_question,
            supplier_name=supplier_name,
            auditor_name=auditor_name,
            action_items=action_items,
            error="This audit has been submitted and cannot be edited."
        )

    error = None

    if request.method == "POST":
        scores = {}
        for key, value in request.form.items():
            if key.startswith("score_"):
                finding_id = int(key.split("_")[1])
                try:
                    scores[finding_id] = float(value)
                except ValueError:
                    scores[finding_id] = None

        action_items = request.form.getlist("action_item")

        submit_final = "submit_final" in request.form

        # Mandatory question validation
        if submit_final:
            missing = []
            for group in template.groups:
                for q in group.questions:
                    if q.mandatory == 'Y':
                        finding = findings_by_question.get(q.question_id)
                        if finding and (finding.finding_id not in scores or scores[finding.finding_id] is None):
                            missing.append(q.question_text)
            if missing:
                error = f"Cannot submit final. Mandatory questions missing scores: {', '.join(missing)}"
            else:
                # Save audit
                AuditService.save_audit_scores(audit_id, scores, submit_final=True)
                AuditService.save_action_items(audit_id, action_items, True)
                flash("Audit submitted successfully!", "success")
                return redirect(url_for("view_audit", audit_id=audit_id))

        else:
            # Save draft
            AuditService.save_audit_scores(audit_id, scores, submit_final=False)
            AuditService.save_action_items(audit_id, action_items, submit_final=False)
            flash("Draft saved successfully!", "success")
            return redirect(url_for("edit_audit", audit_id=audit_id))

    return render_template(
        "edit_audit.html",
        audit=audit,
        template=template,
        findings_by_question=findings_by_question,
        supplier_name=supplier_name,
        auditor_name=auditor_name,
        action_items=action_items,
        error=error
    )

@app.route("/view_audit/<int:audit_id>")
def view_audit(audit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get('supplier_id') is not None:
        return "Unauthorized", 403

    audit, template, findings_by_question, supplier_name, auditor_name, action_items = AuditService.get_audit_with_findings(audit_id)

    if not audit:
        return "Audit not found", 404

    if audit.draft == 'Y':
        # Prevent viewing drafts here
        return redirect(url_for("edit_audit", audit_id=audit_id))

    return render_template(
        "view_audit.html",
        audit=audit,
        template=template,
        findings_by_question=findings_by_question,
        supplier_name=supplier_name,
        auditor_name=auditor_name,
        action_items=action_items
    )

@app.route("/delete_audit/<int:audit_id>")
def delete_audit(audit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get('supplier_id') is not None:
        return "Unauthorized", 403

    user_id = session["user_id"]

    audit = AuditService.get_audit_by_id(audit_id)

    if not audit:
        return "Audit not found", 404

    if audit.draft == 'N' or audit.auditor_id != user_id:
        # Prevent viewing drafts here
        return "Unauthorized", 403

    AuditService.delete_audit_by_id(audit_id)

    return redirect(url_for("audit_listing"))

@app.route("/audit_listing")
def audit_listing():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    if session.get('supplier_id') is not None:
        return "Unauthorized", 403

    # Fetch all audits by this user
    audits = AuditService.get_audits_by_user(user_id)  # We'll implement this next

    # Fetch supplier names for each audit
    supplier_ids = list({a.supplier_id for a in audits})
    suppliers = {s.supplier_id: s for s in SupplierService.get_suppliers_by_ids(supplier_ids)}

    # Sort drafts first, then by created_ts descending
    audits.sort(key=lambda a: (a.draft != 'Y', -a.created_ts.timestamp()))

    return render_template(
        "audit_listing.html",
        audits=audits,
        suppliers=suppliers
    )

@app.route("/supplier_view_audit/<int:audit_id>", methods=["GET", "POST"])
def supplier_view_audit(audit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    supplier_id = session.get("supplier_id")
    if supplier_id is None:
        return "Unauthorized", 403

    audit, template, findings_by_question, supplier_name, auditor_name, action_items = \
        AuditService.get_audit_with_findings(audit_id)

    if not audit or audit.supplier_id != supplier_id:
        return "Unauthorized", 403

    # ===== HANDLE SUBMIT =====
    if request.method == "POST":

        # Only allow submission if items are in submitted state
        if not all(item.status == "submitted" for item in action_items):
            return "Invalid action", 400

        for item in action_items:
            root = request.form.get(f"root_cause_{item.action_item_id}")
            corr = request.form.get(f"corrective_action_{item.action_item_id}")
            prev = request.form.get(f"preventive_action_{item.action_item_id}")

            ActionItemService.update_supplier_response(
                item.action_item_id,
                root,
                corr,
                prev,
                session["user_id"]
            )

        # Mark all complete
        ActionItemService.mark_all_complete(audit_id)
        audit, template, findings_by_question, supplier_name, auditor_name, action_items = \
            AuditService.get_audit_with_findings(audit_id)

        return render_template(
            "supplier_view_audit.html",
            audit=audit,
            template=template,
            findings_by_question=findings_by_question,
            supplier_name=supplier_name,
            auditor_name=auditor_name,
            action_items=action_items
        )

    return render_template(
        "supplier_view_audit.html",
        audit=audit,
        template=template,
        findings_by_question=findings_by_question,
        supplier_name=supplier_name,
        auditor_name=auditor_name,
        action_items=action_items
    )


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