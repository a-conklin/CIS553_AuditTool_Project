class AuditTemplateQuestion:
    def __init__(self, question_id, group_id, question_text, mandatory):
        self.question_id = question_id
        self.group_id = group_id
        self.question_text = question_text
        self.mandatory = mandatory  # 'Y' / 'N'

    @classmethod
    def from_row(cls, row):
        return cls(
            question_id=row[0],
            group_id=row[1],
            question_text=row[2],
            mandatory=row[3]
        )