import psycopg2
from flask import jsonify

from dbconfig import db_config
from entity.audit_template import AuditTemplate
from entity.audit_template_group import AuditTemplateGroup
from entity.audit_template_question import AuditTemplateQuestion


class AuditTemplateService:

    @staticmethod
    def create_template(data, user_id):
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        try:
            # Build entity tree from input
            template = AuditTemplate(
                template_id=None,
                name=data['name'],
                created_by=user_id
            )

            for g in data.get('groups', []):
                group = AuditTemplateGroup(
                    group_id=None,
                    template_id=None,
                    name=g.get('name'),
                    weight=g.get('weight', 1)
                )

                for q in g.get('questions', []):
                    question = AuditTemplateQuestion(
                        question_id=None,
                        group_id=None,
                        question_text=q.get('text'),
                        mandatory='Y' if q.get('mandatory') else 'N'
                    )
                    group.add_question(question)

                template.add_group(group)

            # Insert template
            cur.execute("""
                   INSERT INTO supplieraudit.Audit_Template (name, created_by)
                   VALUES (%s, %s)
                   RETURNING template_id
               """, (template.name, user_id))

            template_id = cur.fetchone()[0]
            template.template_id = template_id

            # Insert groups + questions
            for group in template.groups:
                cur.execute("""
                       INSERT INTO supplieraudit.Audit_Template_Group
                       (template_id, name, weight, created_by)
                       VALUES (%s, %s, %s, %s)
                       RETURNING group_id
                   """, (
                    template_id,
                    group.name,
                    group.weight,
                    user_id
                ))

                group_id = cur.fetchone()[0]
                group.group_id = group_id

                for q in group.questions:
                    cur.execute("""
                           INSERT INTO supplieraudit.Audit_Template_Question
                           (group_id, question_text, mandatory, created_by)
                           VALUES (%s, %s, %s, %s)
                       """, (
                        group_id,
                        q.question_text,
                        q.mandatory,
                        user_id
                    ))

            conn.commit()
            return {"status": "success", "template_id": template_id}

        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": str(e)}

        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_templates():
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        try:
            cur.execute("""
                   SELECT 
                       t.template_id,
                       t.name,
                       t.created_ts,
                       u.username AS created_by
                   FROM supplieraudit.Audit_Template t
                   LEFT JOIN supplieraudit.users u ON t.created_by = u.id
                   ORDER BY t.created_ts DESC
               """)

            rows = cur.fetchall()
            return [AuditTemplate.from_row(row) for row in rows]

        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_template_by_id(template_id: int) -> AuditTemplate:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        try:
            # Get template info
            cur.execute("""
                    SELECT template_id, name, created_ts, created_by
                    FROM supplieraudit.audit_template
                    WHERE template_id = %s
                """, (template_id,))
            t_row = cur.fetchone()
            if not t_row:
                return None

            template = AuditTemplate.from_row(t_row)

            # Get groups
            cur.execute("""
                    SELECT group_id, template_id, name, weight
                    FROM supplieraudit.audit_template_group
                    WHERE template_id = %s
                    ORDER BY group_id
                """, (template_id,))
            groups_data = cur.fetchall()

            for g_row in groups_data:
                group = AuditTemplateGroup.from_row(g_row)

                # Get questions for group
                cur.execute("""
                        SELECT question_id, group_id, question_text, mandatory
                        FROM supplieraudit.audit_template_question
                        WHERE group_id = %s
                        ORDER BY question_id
                    """, (group.group_id,))
                questions_data = cur.fetchall()

                for q_row in questions_data:
                    question = AuditTemplateQuestion.from_row(q_row)
                    group.add_question(question)

                template.add_group(group)

            return template

        finally:
            cur.close()
            conn.close()