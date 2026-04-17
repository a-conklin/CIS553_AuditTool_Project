from dataclasses import field

from playwright.sync_api import Page, expect
    
def load_test_data(file_path: str):
    data = {}
    with open(file_path, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                data[key.strip()] = value.strip()
    return data

def get_table_rows(page: Page, table_selector: str):
    return page.locator(f"{table_selector} tr")


def get_row_count(page: Page, table_selector: str):
    return get_table_rows(page, table_selector).count()

def get_id_column_index(page: Page, table_selector: str):
    headers = page.locator(f"{table_selector} th")

    for i in range(headers.count()):
        if headers.nth(i).inner_text().strip().lower() == "id":
            return i

    raise Exception("ID column not found")


def get_last_table_id(page: Page, table_selector: str):
    rows = get_table_rows(page, table_selector)
    id_index = get_id_column_index(page, table_selector)

    max_id = -1
    max_row_data = None

    for i in range(rows.count()):
        row = rows.nth(i)
        cells = row.locator("td")

        id_text = cells.nth(id_index).inner_text().strip()
        if not id_text.isdigit():
            continue

    row_id = int(id_text)

    if row_id > max_id:
        max_id = row_id
        max_row_data = [cells.nth(j).inner_text().strip()
                        for j in range(cells.count())]       

    return max_id, max_row_data


def test_create_user(auth_page):
    # Navigate to user managementd
    auth_page.click("text=View Suppliers", timeout=5000)
    auth_page.wait_for_selector("#supplierTable")
    auth_page.wait_for_selector("#supplierTable tr")
    before_count = get_row_count(auth_page, "#supplierTable")
    print("Before count:", before_count)
    
    auth_page.click("text=Add New Supplier", timeout=5000)
    auth_page.wait_for_selector("text=Add New Supplier")     

    auth_page.fill('input[name="name"]', "Test Supplier")
    auth_page.fill('input[name="address"]', "Test Address")
    auth_page.fill('input[name="city"]', "Test City")
    auth_page.fill('input[name="state"]', "Test State")
    auth_page.fill('input[name="country"]', "Test Country")
    auth_page.fill('input[name="zip"]', "12345")
    
    auth_page.click("text=Add Supplier", timeout=5000)
    print("Supplier form submitted")
    
    auth_page.wait_for_selector("#supplierTable")

    expect(get_table_rows(auth_page, "#supplierTable")).to_have_count(before_count + 1)

    after_count = get_row_count(auth_page, "#supplierTable")
    print("After count:", after_count)
    
    assert after_count == before_count + 1, "Row count did not increase"