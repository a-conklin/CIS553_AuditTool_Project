class Audit:
    def __init__(self, audit_id, auditor_id, supplier_id, total_score, draft, created_ts, last_edited_ts):
        self.audit_id = audit_id
        self.auditor_id = auditor_id
        self.supplier_id = supplier_id
        self.total_score = total_score
        self.draft = draft
        self.created_ts = created_ts
        self.last_edited_ts = last_edited_ts

    @classmethod
    def from_row(cls, row):
        return cls(
            audit_id=row[0],
            auditor_id=row[1],
            supplier_id=row[2],
            total_score=row[3],
            draft=row[4],
            created_ts=row[5],
            last_edited_ts=row[6]
        )