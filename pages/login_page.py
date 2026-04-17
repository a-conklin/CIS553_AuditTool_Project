class LoginPage:
    def __init__(self, page):
        self.page = page

    def login(self, email, password):
        self.page.fill('input[name="email"]', email)
        self.page.fill('input[name="password"]', password)

        with self.page.expect_navigation():
            self.page.click('button[type="submit"]')

    def wait_for_dashboard(self):
        self.page.wait_for_selector("text=Welcome, ", timeout=10000)

    def is_logged_in(self):
        try:
            self.page.wait_for_selector("text=Welcome, ", timeout=5000)
            return True
        except:
            return False
