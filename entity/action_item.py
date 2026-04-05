class ActionItem:
    def __init__(
        self,
        action_item_id=None,
        audit_id=None,
        item_text=None,
        root_cause=None,
        corrective_action=None,
        preventive_action=None,
        status="draft",
        responder_id=None
    ):
        self.action_item_id = action_item_id
        self.audit_id = audit_id
        self.item_text = item_text
        self.root_cause = root_cause
        self.corrective_action = corrective_action
        self.preventive_action = preventive_action
        self.status = status
        self.responder_id = responder_id

    @classmethod
    def from_row(cls, row):
        return cls(
            action_item_id=row[0],
            audit_id=row[1],
            item_text=row[2],
            root_cause=row[3],
            corrective_action=row[4],
            preventive_action=row[5],
            status=row[6],
            responder_id=row[7]
        )