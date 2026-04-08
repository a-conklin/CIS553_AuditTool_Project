import psycopg2
from dbconfig import db_config
from entity.action_item import ActionItem


class ActionItemService:
    @staticmethod
    def get_action_items_for_audit(audit_id):

        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT action_item_id, audit_id, item_text, root_cause,
                       corrective_action, preventive_action, status, responder_id
                FROM supplieraudit.action_item
                WHERE audit_id = %s
            """, (audit_id,))

            action_items = [ActionItem.from_row(r) for r in cur.fetchall()]

            return action_items

        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_action_item_count_for_audit(audit_id):
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT COUNT(*)
                FROM supplieraudit.action_item
                WHERE audit_id = %s AND status = 'submitted'
            """, (audit_id,))

            count = cur.fetchone()[0]
            return count

        finally:
            cur.close()
            conn.close()

    @staticmethod
    def update_supplier_response(action_item_id, root, corr, prev, responder_id):
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE supplieraudit.action_item
                SET root_cause = %s,
                    corrective_action = %s,
                    preventive_action = %s,
                    responder_id = %s
                WHERE action_item_id = %s
            """, (root, corr, prev, responder_id, action_item_id))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def mark_all_complete(audit_id):
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE supplieraudit.action_item
                SET status = 'complete'
                WHERE audit_id = %s
            """, (audit_id,))
            conn.commit()
        finally:
            cur.close()
            conn.close()