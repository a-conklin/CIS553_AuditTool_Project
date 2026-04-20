import grp
from random import random, choice
from time import sleep
from tokenize import group
import pandas as pd
import test_utils, test_login
from playwright.sync_api import expect

def test_create_audit(admin_auth_page):
    page = admin_auth_page

    page.click("text=View Your Audits", timeout=5000)
    page.wait_for_selector("text=My Audits")
    
    print ("My Audits page loaded")

    page.click("text=Create New Audit", timeout=5000)
    page.wait_for_selector("text=Create New Audit")

    print ("Create new audit page loaded")
    page.locator("select[name='supplier_id']").select_option(
        label="Shannon Ashley Mendonca (Dayton, OH)"
    )
    print ("Supplier selected")
    page.locator("select[name='template_id']").select_option(
        label="Temp"
    )
    print ("Template selected")
    page.click("text=Create Draft Audit", timeout=5000)
    page.wait_for_selector("text=Audit of", timeout=10000)
    
    test_utils.select_weight(page)
    test_utils.add_action_item(page)
    page.click("text=Submit Final")
   
    expect(page.locator("text=Final Audit Score")).to_be_visible()
    print("Audit created and run.")
    
def test_create_draft_audit(admin_auth_page):
    page = admin_auth_page

    page.click("text=View Your Audits", timeout=5000)
    page.wait_for_selector("text=My Audits")
    
    print ("My Audits page loaded")

    page.click("text=Create New Audit", timeout=5000)
    page.wait_for_selector("text=Create New Audit")

    print ("Create new audit page loaded")
    page.locator("select[name='supplier_id']").select_option(
        label="Shannon Ashley Mendonca (Dayton, OH)"
    )
    print ("Supplier selected")
    page.locator("select[name='template_id']").select_option(
        label="Temp"
    )
    print ("Template selected")
    page.click("text=Create Draft Audit", timeout=5000)
    page.wait_for_selector("text=Audit of", timeout=10000)
    
    test_utils.select_weight(page)
    test_utils.add_action_item(page)
    test_utils.save_draft(page)
    test_utils.click_back(page)
    
def test_delete_audit(admin_auth_page):
    page = admin_auth_page

    page.click("text=View Your Audits", timeout=5000)
    page.wait_for_selector("text=My Audits")
    print ("My Audits page loaded")
    
    page.locator("table tbody tr").first.locator(
    "a:has-text('Delete'):visible, button:has-text('Delete'):visible"
    ).click()
    
    test_utils.delete_audit_draft(page)
    page.wait_for_selector("text=My Audits", timeout=5000)
    print ("Back to My Audits page")
    
def test_goto_homepage(admin_auth_page):
    test_utils.click_home(admin_auth_page)
    
def test_goto_login(admin_auth_page):
    test_login.logout(admin_auth_page)

    





