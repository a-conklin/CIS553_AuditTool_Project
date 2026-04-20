import test_login

def test_supplier_view_audit(user_auth_page):
    page = user_auth_page

    page.wait_for_selector("text=Your Supplier Information", timeout=10000)
    print ("Supplier dashboard loaded")
    
    page.locator("table.audit-table tbody tr", has_text="Audit performed on")\
        .locator("a")\
            .click()

    print("Supplier view permissions test passed.")
    test_login.logout(page)