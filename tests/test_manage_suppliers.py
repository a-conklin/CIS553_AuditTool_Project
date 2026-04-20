import csv
import test_utils, test_login
from playwright.sync_api import expect
    

def test_add_new_supplier(admin_auth_page):
    admin_auth_page.click("text=View Suppliers", timeout=5000)
    admin_auth_page.wait_for_selector("#supplierTable")
    admin_auth_page.wait_for_selector("#supplierTable tr")
    before_count = test_utils.get_row_count(admin_auth_page, "#supplierTable")
    print("Before count:", before_count)
    
    with open("/Users/sam/Code/Web Development/CIS553_AuditTool_Project/tests/supplier_data.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            admin_auth_page.click("text=Add New Supplier", timeout=5000)
            admin_auth_page.wait_for_selector("text=Add New Supplier")    
            
            admin_auth_page.fill('input[name="name"]', row["supplier_name"])
            admin_auth_page.fill('input[name="address"]', row["address"])
            admin_auth_page.fill('input[name="city"]', row["city"])
            admin_auth_page.fill('input[name="state"]', row["state"])
            admin_auth_page.fill('input[name="country"]', row["country"])
            admin_auth_page.fill('input[name="zip"]', row["zip"])

            admin_auth_page.click("button[type='submit']")

            admin_auth_page.wait_for_selector("#supplierTable")

        print(expect(test_utils.get_table_rows(admin_auth_page, "#supplierTable")).to_have_count(before_count + 50))

        after_count = test_utils.get_row_count(admin_auth_page, "#supplierTable")
        print("After count:", after_count)
        
        assert after_count == before_count + 50, "Row count did not increase"
    
def test_goto_homepage(admin_auth_page):
    test_utils.click_home(admin_auth_page)
    
def test_goto_login(admin_auth_page):
    test_login.logout(admin_auth_page)


