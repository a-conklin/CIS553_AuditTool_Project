class AuditTemplate:
    def __init__(self, template_id, name, created_ts=None, created_by=None):
        self.template_id = template_id
        self.name = name
        self.created_ts = created_ts
        self.created_by = created_by
        self.groups = []

    def add_group(self, group):
        self.groups.append(group)

    @classmethod
    def from_row(cls, row):
        return cls(
            template_id=row[0],
            name=row[1],
            created_ts=row[2],
            created_by=row[3]
        )