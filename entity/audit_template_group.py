class AuditTemplateGroup:
    def __init__(self, group_id, template_id, name, weight=1):
        self.group_id = group_id
        self.template_id = template_id
        self.name = name
        self.weight = weight
        self.questions = []

    def add_question(self, question):
        self.questions.append(question)

    @classmethod
    def from_row(cls, row):
        return cls(
            group_id=row[0],
            template_id=row[1],
            name=row[2],
            weight=row[3]
        )