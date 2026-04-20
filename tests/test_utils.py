from playwright.sync_api import Page
import pandas as pd
from random import choice, random

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


def fill_questions(page):
    df = pd.read_csv("/Users/sam/Code/Web Development/CIS553_AuditTool_Project/tests/oem_supplier_audit_questions.csv")
    questions = df["question_text"].dropna().tolist()
    
    if not questions:
        print("No questions found in CSV.")
        return 
    
    question = choice(questions)    
    print(question)
    question_inputs = page.locator("input[placeholder='Question text'], textarea[placeholder='Question text']")
    last_input = question_inputs.nth(question_inputs.count() - 1)
    last_input.fill(question)
    print(f"Question filled: {question}")  
  
    
def fill_groupname(page):
    df = pd.read_csv("/Users/sam/Code/Web Development/CIS553_AuditTool_Project/tests/supplier_groups.csv")
    grp = df["group_name"].dropna().tolist()
    
    if not grp:
        print("No groups found in CSV.")
        return
    
    print(grp)
    rand_grp = choice(grp)
    print(rand_grp)
    group_inputs = page.locator("input[placeholder='Group Name']")
    last_input = group_inputs.nth(group_inputs.count() - 1)
    last_input.fill(rand_grp)
    print(f"Group filled: {rand_grp}")
  

def add_action_item(page):
    page.locator("text=Add Action Item").click()
    page.locator("textarea").first.fill("Test Action Item")
    
def save_draft(page):
    page.click("text=Save Draft", timeout=5000)
    print ("Draft saved")
    
def submit_final(page):
    page.click("text=Submit Final", timeout=5000)
    page.wait_for_selector("text=Final Audit Score", timeout=5000)
    print ("Final audit submitted")

def back_to_audit_list(page):
    page.click("text=Back to Audit List", timeout=5000)
    page.wait_for_selector("text=My Audits", timeout=5000)
    print ("Back to audit list")

def select_weight(page):
    page.fill('input[type="number"]', str(round(random() * 10, 1)))
    print ("Weight selected")
        
def delete_audit_draft(page):
    print ("Attempting to delete audit draft")
    page.once("dialog", handle_dialog)
    page.click("text=Delete", timeout=5000)
    print ("Audit deleted")
   
def handle_dialog(dialog):
    assert "Are you sure you want to delete this audit?" in dialog.message
    dialog.accept()
    print ("Dialog accepted")

def click_back(page):
    page.click("text=Back", timeout=5000)
    page.wait_for_selector("text=My Audits", timeout=5000)
    print ("Back to audit list")

def click_home(page):
    page.click("text=Home", timeout=5000)
    page.wait_for_selector("h1:has-text('Welcome, ')", timeout=5000)
    print ("Back to supplier dashboard")
    
def click_edit(page):
    rows = page.locator("table.audit-table tbody tr")
    count = rows.count()
    print(count)

    highest_id = -1
    target_row = None

    for i in range(count):
        row = rows.nth(i)
        ths = row.locator("td")
        if ths.count() == 1:
            continue
        audit_id_text = ths.first.inner_text().strip()
        if not audit_id_text.isdigit():
            continue
        audit_id = int(audit_id_text)
        if audit_id > highest_id:
            highest_id = audit_id
            target_row = row
            target_row.locator("a:has-text('Edit'):visible, button:has-text('Edit'):visible").click()
            print(f"Clicked Edit for audit ID {audit_id}")
            break
        