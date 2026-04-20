from pages.login_page import LoginPage

def test_invalid_login(base_page):
    login = LoginPage(base_page)
    login.login("wrong@example.com", "wrongpass")
    base_page.wait_for_selector("text=Invalid", timeout=5000)
    
    assert base_page.locator("text=Invalid").is_visible()
    print("Test invalid login and run.")


def test_valid_login(base_page):
    login = LoginPage(base_page)
    login.login("supplier@test.com", "123")
    login.wait_for_dashboard()
    
    assert login.is_logged_in()
    print("Test valid login and run.")

    
def logout(page):
    page.click("text=Logout", timeout=5000)
    
    assert page.locator("text=Supplier Audit Login").is_visible()
    print("Test logout and run.")