import psycopg2
from dbconfig import db_config
from entity.action_item import ActionItem
from entity.audit import Audit
from entity.audit_finding import AuditFinding
from service.audit_template_service import AuditTemplateService


class AuditService:

    @staticmethod
    def get_audits_for_supplier(supplier_id):
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT audit_id, auditor_id, supplier_id, total_score, draft, created_ts, last_edited_ts
                FROM supplieraudit.audit
                WHERE supplier_id = %s AND draft = 'N'
                ORDER BY created_ts DESC
            """, (supplier_id,))

            rows = cur.fetchall()

            return [Audit.from_row(row) for row in rows]

        finally:
            cur.close()
            conn.close()

    @staticmethod
    def create_draft_audit(auditor_id: int, supplier_id: int, template_id: int) -> int:
        """
        Creates a new draft audit and prepopulates audit_findings
        from the selected template.
        Returns the new audit_id.
        """
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        try:
            # Create the audit record
            cur.execute("""
                    INSERT INTO supplieraudit.audit (auditor_id, supplier_id, total_score, draft, created_ts, last_edited_ts)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                    RETURNING audit_id
                """, (auditor_id, supplier_id, 0, 'Y'))
            audit_id = cur.fetchone()[0]

            # Fetch all questions from the selected template
            cur.execute("""
                    SELECT q.question_id
                    FROM supplieraudit.audit_template_group g
                    JOIN supplieraudit.audit_template_question q ON q.group_id = g.group_id
                    WHERE g.template_id = %s
                    ORDER BY g.group_id, q.question_id
                """, (template_id,))
            questions = cur.fetchall()

            # Insert a blank audit_finding for each question
            for q_row in questions:
                question_id = q_row[0]
                cur.execute("""
                        INSERT INTO supplieraudit.audit_finding (audit_id, question_id, score, last_edited_ts)
                        VALUES (%s, %s, %s, NOW())
                    """, (audit_id, question_id, 0))

            conn.commit()
            return audit_id

        except Exception as e:
            conn.rollback()
            raise e

        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_audit_with_findings(audit_id):
        """
        Returns (audit_entity, template_entity, findings_by_question dict)
        """
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT audit_id, auditor_id, supplier_id, total_score, draft, created_ts, last_edited_ts
                FROM supplieraudit.audit
                WHERE audit_id = %s
            """, (audit_id,))
            a_row = cur.fetchone()
            if not a_row:
                return None, None, None

            audit = Audit.from_row(a_row)

            cur.execute("""
                    SELECT q.group_id
                    FROM supplieraudit.audit_finding f
                    JOIN supplieraudit.audit_template_question q ON q.question_id = f.question_id
                    WHERE f.audit_id = %s
                    LIMIT 1
                """, (audit_id,))
            group_id_row = cur.fetchone()
            template_id = None
            if group_id_row:
                cur.execute("""
                        SELECT template_id
                        FROM supplieraudit.audit_template_group
                        WHERE group_id = %s
                    """, (group_id_row[0],))
                template_id = cur.fetchone()[0]

            template = AuditTemplateService.get_template_by_id(template_id)

            cur.execute("""
                    SELECT finding_id, audit_id, score, question_id
                    FROM supplieraudit.audit_finding
                    WHERE audit_id = %s
                """, (audit_id,))
            findings_rows = cur.fetchall()

            findings_by_question = {r[3]: AuditFinding.from_row(r) for r in findings_rows}

            # Get supplier + auditor names
            cur.execute("""
                SELECT s.name, u.username
                FROM supplieraudit.audit a
                JOIN supplieraudit.supplier s ON a.supplier_id = s.supplier_id
                JOIN supplieraudit.users u ON a.auditor_id = u.id
                WHERE a.audit_id = %s
            """, (audit_id,))

            name_row = cur.fetchone()
            supplier_name = name_row[0] if name_row else "Unknown Supplier"
            auditor_name = name_row[1] if name_row else "Unknown Auditor"

            cur.execute("""
                SELECT a.action_item_id, a.audit_id, a.item_text, a.root_cause,
                       a.corrective_action, a.preventive_action, a.status, u.username
                FROM supplieraudit.action_item a
                LEFT JOIN supplieraudit.users u ON a.responder_id = u.id
                WHERE audit_id = %s
            """, (audit_id,))

            action_items = [ActionItem.from_row(r) for r in cur.fetchall()]

            return audit, template, findings_by_question, supplier_name, auditor_name, action_items

        finally:
            cur.close()
            conn.close()

    @staticmethod
    def save_audit_scores(audit_id, scores_dict, submit_final=False):
        """
        Updates scores for the audit and recalculates total_score using group weights
        """
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        try:
            # Update individual scores
            for finding_id, score in scores_dict.items():
                cur.execute("""
                        UPDATE supplieraudit.audit_finding
                        SET score = %s, last_edited_ts = NOW()
                        WHERE finding_id = %s
                    """, (score, finding_id))

            # Recalculate weighted total score
            cur.execute("""
                    SELECT g.group_id, g.weight, f.score
                    FROM supplieraudit.audit_finding f
                    JOIN supplieraudit.audit_template_question q ON q.question_id = f.question_id
                    JOIN supplieraudit.audit_template_group g ON g.group_id = q.group_id
                    WHERE f.audit_id = %s
                """, (audit_id,))

            group_scores = {}
            group_weights = {}

            for group_id, weight, score in cur.fetchall():
                if group_id not in group_scores:
                    group_scores[group_id] = []
                    group_weights[group_id] = weight
                group_scores[group_id].append(score)

            total_weighted_score = 0
            total_weights = 0
            for gid, scores in group_scores.items():
                avg = sum(scores) / len(scores) if scores else 0
                total_weighted_score += avg * group_weights[gid]
                total_weights += group_weights[gid]

            final_score = (total_weighted_score / total_weights) if total_weights else 0

            # Update audit record
            cur.execute("""
                    UPDATE supplieraudit.audit
                    SET total_score = %s,
                        draft = %s,
                        last_edited_ts = NOW()
                    WHERE audit_id = %s
                """, (final_score, 'N' if submit_final else 'Y', audit_id))

            conn.commit()
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_audits_by_user(user_id):
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT audit_id, auditor_id, supplier_id, total_score, draft, created_ts, last_edited_ts
                FROM supplieraudit.audit
                WHERE auditor_id = %s
            """, (user_id,))
            rows = cur.fetchall()
            return [Audit.from_row(row) for row in rows]
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_audit_by_id(audit_id):
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        try:
            cur.execute("""
                       SELECT audit_id, auditor_id, supplier_id, total_score, draft, created_ts, last_edited_ts
                       FROM supplieraudit.audit
                       WHERE audit_id = %s
                   """, (audit_id,))
            a_row = cur.fetchone()
            if not a_row:
                return None, None, None

            audit = Audit.from_row(a_row)
            return audit
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def delete_audit_by_id(audit_id):
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        try:
            cur.execute("""
                           DELETE 
                           FROM supplieraudit.audit
                           WHERE audit_id = %s and draft = 'Y'
                       """, (audit_id,))


            conn.commit()
            return {"status": "success"}

        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": str(e)}

        finally:
            cur.close()
            conn.close()

    @staticmethod
    def save_action_items(audit_id, action_items_texts, submit_final=False):
        """
        action_items_texts: list of strings
        """
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        try:
            #Delete existing items
            cur.execute("""
                DELETE FROM supplieraudit.action_item
                WHERE audit_id = %s
            """, (audit_id,))

            #Insert fresh items
            status = 'submitted' if submit_final else 'draft'

            for text in action_items_texts:
                if text.strip():
                    cur.execute("""
                        INSERT INTO supplieraudit.action_item
                        (audit_id, item_text, status)
                        VALUES (%s, %s, %s)
                    """, (audit_id, text.strip(), status))

            conn.commit()
            return {"status": "success"}

        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": str(e)}

        finally:
            cur.close()
            conn.close()