"""Login and registration forms.

The backend is mocked with page.route (any host, path /auth/...), so no real account is created and the
tests check exactly what the form sends and how the UI reacts to each server answer.
"""
import json

import pytest
from playwright.sync_api import expect

from pages.auth_pages import LoginPage, RegisterPage


def mock_api(page, path: str, status: int, body: dict | None = None):
    calls = []

    def handler(route):
        calls.append(route.request)
        route.fulfill(status=status, content_type="application/json", body=json.dumps(body or {}))

    page.route(f"**{path}", handler)
    return calls


@pytest.fixture
def login(page):
    return LoginPage(page).open()


@pytest.fixture
def register(page):
    return RegisterPage(page).open()


# ---------- login ----------

@pytest.mark.smoke
def test_login_empty_form_shows_errors_and_sends_nothing(login):
    calls = mock_api(login.page, "/auth/login", 200)
    login.submit()
    expect(login.field_errors).to_have_text(["Email є обов'язковим", "Пароль є обов'язковим"])
    assert calls == []


def test_login_email_without_domain_zone_is_rejected(login):
    # 'qa@example' passes the browser's own check, so the app's validation is what stops it
    login.login("qa@example", "secret123")
    expect(login.field_errors.first).to_have_text("Будь ласка, введіть дійсну адресу електронної пошти")


def test_field_error_disappears_when_user_types(login):
    login.submit()
    expect(login.page.locator(".error-text", has_text="Email")).to_have_count(1)
    login.input("email").fill("a")
    expect(login.page.locator(".error-text", has_text="Email")).to_have_count(0)


def test_password_visibility_toggle(login):
    expect(login.input("password")).to_have_attribute("type", "password")
    login.page.get_by_role("button", name="Show password").click()
    expect(login.input("password")).to_have_attribute("type", "text")


def test_login_wrong_credentials_401(login):
    calls = mock_api(login.page, "/auth/login", 401)
    login.login("qa@example.com", "wrong-pass")
    expect(login.form_error).to_have_text("Невірний email або пароль")
    assert json.loads(calls[0].post_data) == {"email": "qa@example.com", "password": "wrong-pass"}
    assert login.page.evaluate("localStorage.getItem('token')") is None


def test_login_server_error_500_shows_generic_message(login):
    mock_api(login.page, "/auth/login", 500)
    login.login("qa@example.com", "secret123")
    expect(login.form_error).to_have_text("Помилка входу. Спробуйте пізніше.")


def test_login_server_error_shows_message_from_backend(login):
    mock_api(login.page, "/auth/login", 423, {"message": "Акаунт заблоковано"})
    login.login("qa@example.com", "secret123")
    expect(login.form_error).to_have_text("Акаунт заблоковано")


def test_login_success_saves_session(login):
    user = {"id": "1", "email": "qa@example.com", "firstName": "QA", "lastName": "User"}
    mock_api(login.page, "/auth/login", 200, {"token": "test-token", "user": user})
    login.login("qa@example.com", "secret123")
    login.page.wait_for_function("localStorage.getItem('token') === 'test-token'")
    assert json.loads(login.page.evaluate("localStorage.getItem('user')"))["email"] == "qa@example.com"


@pytest.mark.bug
@pytest.mark.xfail(reason="BUG-11: when the server is unreachable the user sees a raw 'Failed to fetch' error")
def test_login_network_failure_shows_friendly_message(login):
    login.page.route("**/auth/login", lambda route: route.abort())
    login.login("qa@example.com", "secret123")
    expect(login.form_error).to_be_visible()
    expect(login.form_error).not_to_have_text("Failed to fetch")


@pytest.mark.bug
@pytest.mark.xfail(reason="BUG-13: divider on the login page is 'ОR' with a Cyrillic 'О' (register page has Latin 'OR')")
def test_login_divider_text(login):
    expect(login.page.locator(".divider span")).to_have_text("OR")


# ---------- register ----------

@pytest.mark.parametrize(
    "username, email, password, repeat, error",
    [
        ("", "qa@example.com", "password123", "password123", "Ім'я користувача є обов'язковим"),
        ("А", "qa@example.com", "password123", "password123", "Ім'я має містити не менше 2 символів"),
        ("Олена", "qa@example", "password123", "password123", "Будь ласка, введіть дійсну адресу електронної пошти"),
        ("Олена", "qa@example.com", "1234567", "1234567", "Пароль має містити не менше 8 символів"),
        ("Олена", "qa@example.com", "password123", "password124", "Паролі не співпадають"),
    ],
    ids=["empty-name", "short-name", "bad-email", "short-password", "passwords-differ"],
)
def test_register_validation(register, username, email, password, repeat, error):
    calls = mock_api(register.page, "/auth/register", 201, {"token": "t"})
    register.register(username, email, password, repeat)
    expect(register.page.locator(".error-text", has_text=error)).to_have_count(1)
    assert calls == []


def test_register_password_of_exactly_8_chars_is_accepted(register):
    calls = mock_api(register.page, "/auth/register", 201, {"token": "t"})
    register.register("Олена", "qa@example.com", "12345678", "12345678")
    expect(register.field_errors).to_have_count(0)
    register.page.wait_for_timeout(1000)
    assert len(calls) == 1


def test_register_existing_email_409(register):
    mock_api(register.page, "/auth/register", 409)
    register.register("Олена", "taken@example.com", "password123", "password123")
    expect(register.form_error).to_have_text("Користувач з такою електронною поштою вже існує")


def test_register_success_sends_data_and_saves_token(register):
    calls = mock_api(register.page, "/auth/register", 201, {"token": "new-token"})
    register.register("Олена", "new@example.com", "password123", "password123")
    register.page.wait_for_function("localStorage.getItem('token') === 'new-token'")
    payload = json.loads(calls[0].post_data)
    assert payload["username"] == "Олена"
    assert payload["email"] == "new@example.com"
