from .base import BasePage


class _AuthForm(BasePage):
    def submit(self):
        self.page.locator("button.submit-btn").click()

    def input(self, name: str):
        return self.page.locator(f"input[name='{name}']")

    @property
    def field_errors(self):
        return self.page.locator(".error-text")

    @property
    def form_error(self):
        return self.page.locator(".error-message")


class LoginPage(_AuthForm):
    route = "/login"

    def login(self, email: str, password: str):
        self.input("email").fill(email)
        self.input("password").fill(password)
        self.submit()


class RegisterPage(_AuthForm):
    route = "/register"

    def register(self, username: str, email: str, password: str, repeat: str):
        self.input("username").fill(username)
        self.input("email").fill(email)
        self.input("password").fill(password)
        self.input("repeatPassword").fill(repeat)
        self.submit()
