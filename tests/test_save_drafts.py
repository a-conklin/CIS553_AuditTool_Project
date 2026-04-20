import test_utils, test_login
from playwright.sync_api import expect

def test_delete_draft_audit(admin_auth_page):
    page = admin_auth_page

    page.click("text=View Your Audits", timeout=5000)
    page.wait_for_selector("text=My Audits")
    print ("My Audits page loaded")
    
    test_utils.click_edit(page)
    page.locator("text=Audit of").wait_for(timeout=5000)
    print ("Audit details page loaded")
    
    test_utils.delete_audit_draft(page)
    page.wait_for_selector("text=My Audits", timeout=5000)
    print ("Back to My Audits page")
 #Move to new file page   
def test_edit_submit_audit(admin_auth_page):
    page = admin_auth_page

    page.click("text=View Your Audits", timeout=5000)
    page.wait_for_selector("text=My Audits")
    print ("My Audits page loaded")
    
    test_utils.click_edit(page)
    page.locator("text=Audit of").wait_for(timeout=5000)
    print ("Audit details page loaded")
    
    test_utils.submit_final(page)
    expect(page.locator("text=Final Audit Score")).to_be_visible()
    print("Audit created and run.")
    
def test_edit_save_draft_audit(admin_auth_page):
    page = admin_auth_page

    page.click("text=View Your Audits", timeout=5000)
    page.wait_for_selector("text=My Audits")
    print ("My Audits page loaded")
    
    test_utils.click_edit(page)
    page.locator("text=Audit of").wait_for(timeout=5000)
    print ("Audit details page loaded")
    
    test_utils.select_weight(page)
    test_utils.add_action_item(page)
    test_utils.save_draft(page)
    test_utils.click_back(page)
    
def test_goto_homepage(admin_auth_page):
    test_utils.click_home(admin_auth_page)
    
def test_goto_login(admin_auth_page):
    test_login.logout(admin_auth_page)
