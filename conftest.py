import pytest
from pages.login_page import LoginPage
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def base_page(page):
    page.goto(BASE_URL)
    return page

@pytest.fixture(scope="function")
def admin_auth_page(page):
    page.goto(BASE_URL)
    login = LoginPage(page)
    login.login("admin@test.com", "123")
    return page

@pytest.fixture(scope="function")
def user_auth_page(page):
    page.goto(BASE_URL)
    login = LoginPage(page)
    login.login("supplier@test.com", "123")
    return page

@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL
