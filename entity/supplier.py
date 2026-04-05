class Supplier:
    def __init__(self, supplier_id, name, address, city, state, country, zip_code):
        self.supplier_id = supplier_id
        self.name = name
        self.address = address
        self.city = city
        self.state = state
        self.country = country
        self.zip = zip_code

    @classmethod
    def from_row(cls, row):
        return cls(
            supplier_id=row[0],
            name=row[1],
            address=row[2],
            city=row[3],
            state=row[4],
            country=row[5],
            zip_code=row[6]
        )