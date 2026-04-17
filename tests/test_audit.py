from playwright.sync_api import expect

def test_create_audit(auth_page):
    page = auth_page

    page.click("text=View Your Audits", timeout=5000)
    page.wait_for_selector("text=My Audits")
    
    print ("My Audits page loaded")

    page.click("text=Create New Audit", timeout=5000)
    page.wait_for_selector("text=Create New Audit")

    print ("Create new audit page loaded")
    # page.wait_for_selector("select[name='Create New Audit']")
    page.locator("select[name='supplier_id']").select_option(
        label="Shannon Ashley Mendonca (Dayton, OH)"
    )
    print ("Supplier selected")
    page.locator("select[name='template_id']").select_option(
        label="Temp"
    )
    print ("Template selected")
    page.click("text=Create Draft Audit", timeout=10000)
    page.wait_for_selector("text=Audit of", timeout=10000)
    
    page.locator("text=Add Action Item").click()
    page.locator("textarea").first.fill("Test Action Item")
    page.locator("text=Submit Final").click()

    expect(page.locator("text=Final Audit Score")).to_be_visible()
    print("Audit created and run.")


def test_audit_template_create(auth_page):
    page = auth_page

    page.click("text=View Templates", timeout=5000)
    page.click("text=Add New Template")
    print ("Template page loaded")

    # page.wait_for_selector('input[name="templateName"]')
    
    page.fill('input[type="text"]', "templateName", timeout=5000)
    print ("Field template name filled")
    page.fill('input[type="text"]', "GRP", timeout=5000)
    print ("Group name filled")
    page.fill('input[type="text"]', "Q1", timeout=5000)
    print ("Question text filled")
    

    page.click("text=Save Template")
    print ("Template saved")

    
