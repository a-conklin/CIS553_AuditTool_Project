import test_utils, test_login

def test_create_basic_template(admin_auth_page):
    page = admin_auth_page

    page.click("text=View Templates", timeout=5000)
    page.click("text=Add New Template")
    print ("Template page loaded")
    
    page.fill('input[type="text"]', "templateName", timeout=5000)
    print ("Field template name filled")

    page.fill('input[type="text"]', "GRP", timeout=5000)
    print ("Group name filled")
    page.fill('input[type="text"]', "Q1", timeout=5000)
    print ("Question text filled")
    
    page.click("text=Save Template")
    print ("Template saved")

def test_create_advanced_audit_template(admin_auth_page):
    page = admin_auth_page

    page.click("text=View Templates", timeout=5000)
    page.click("text=Add New Template")
    print ("Template page loaded")
    
    page.fill('input[id="templateName"]', "Test Industrial Template", timeout=5000)
    print ("Field template name filled")
    test_utils.fill_questions(page)
    test_utils.fill_groupname(page)
    test_utils.fill_questions(page)
    page.locator("text=Add Group").click()
    test_utils.fill_groupname(page)

    page.click("text=Save Template")
    print ("Template saved")
    
def test_delete_audit_template(admin_auth_page):
    page = admin_auth_page

    page.click("text=View Templates", timeout=5000)
    page.wait_for_selector("text=Audit Templates")
    print ("Template list page loaded")
    
    row = page.locator("table tbody tr").first
    row.locator("a").first.click()
    
    page.locator("button:has-text('Delete Template')").click()
    print ("Delete button clicked")
    
    page.wait_for_selector("text=Create Audit Template", timeout=5000)
    print ("Back to Create Audit Template list page")


def test_abort_delete_template(admin_auth_page):
    page = admin_auth_page

    page.click("text=View Templates", timeout=5000)
    page.wait_for_selector("text=Audit Templates")
    print ("Template list page loaded")
    
    row = page.locator("table tbody tr").first
    row.locator("a").first.click()
    
    page.locator("button:has-text('Back to Template List')").click()
    print ("Delete button clicked")
    
    page.wait_for_selector("text=Audit Templates", timeout=5000)
    print ("Back to Audit Template list page")
    
def test_goto_homepage(admin_auth_page):
    test_utils.click_home(admin_auth_page)
    
def test_goto_login(admin_auth_page):
    test_login.logout(admin_auth_page)
