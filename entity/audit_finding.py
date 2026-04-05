class AuditFinding:
    def __init__(self, finding_id=None, audit_id=None, question_id=None, score=0):
        self.finding_id = finding_id
        self.audit_id = audit_id
        self.question_id = question_id
        self.score = score

    @classmethod
    def from_row(cls, row):
        return cls(
            finding_id=row[0],
            audit_id=row[1],
            score=row[2],
            question_id=row[3]
        )