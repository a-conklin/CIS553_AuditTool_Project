import psycopg2
from dbconfig import db_config
from entity.supplier import Supplier


class SupplierService:

    @staticmethod
    def get_supplier_by_id(supplier_id):
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT supplier_id, name, address, city, state, country, zip
                FROM supplieraudit.supplier
                WHERE supplier_id = %s
            """, (supplier_id,))

            row = cur.fetchone()

            if not row:
                return None

            return Supplier.from_row(row)

        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_all_suppliers():
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        try:
            cur.execute("""
                   SELECT supplier_id, name, address, city, state, country, zip
                   FROM supplieraudit.supplier
                   ORDER BY name
               """)

            rows = cur.fetchall()
            return [Supplier.from_row(row) for row in rows]

        finally:
            cur.close()
            conn.close()

    @staticmethod
    def create_supplier(data, user_id):
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        try:
            cur.execute("""
                   INSERT INTO supplieraudit.supplier
                   (name, address, city, state, country, zip, created_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
               """, (
                data.get('name'),
                data.get('address', ''),
                data.get('city'),
                data.get('state'),
                data.get('country'),
                data.get('zip', ''),
                user_id
            ))

            conn.commit()
            return {"status": "success"}

        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": str(e)}

        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_suppliers_by_ids(supplier_ids):
        """
        Returns a list of Supplier objects for the given list of supplier_ids.
        """
        if not supplier_ids:
            return []

        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        try:
            # Use %s with psycopg2's "IN" syntax by passing a tuple
            query = f"""
                SELECT supplier_id, name, address, city, state, country, zip
                FROM supplieraudit.supplier
                WHERE supplier_id IN %s
            """
            cur.execute(query, (tuple(supplier_ids),))
            rows = cur.fetchall()
            return [Supplier.from_row(row) for row in rows]

        finally:
            cur.close()
            conn.close()