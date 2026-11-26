import re

from playwright.sync_api import expect

from .base import BasePage


def money(text: str) -> int:
    return int(re.sub(r"\D", "", text))


class CheckoutPage(BasePage):
    route = "/checkout"

    @property
    def heading(self):
        return self.page.get_by_role("heading", level=1)

    def field(self, label: str):
        return self.page.get_by_label(label, exact=True)

    def fill_customer(self, first="Тест", last="Тестенко", phone="+380501112233", email="qa@example.com"):
        self.field("Ім'я").fill(first)
        self.field("Прізвище").fill(last)
        self.field("Номер телефону").fill(phone)
        self.field("Електронна пошта").fill(email)

    def choose(self, option: str):
        """Delivery / payment radio. Custom-styled radios: the visual span covers the input."""
        self.page.get_by_role("radio", name=option).check(force=True)

    def submit(self):
        self.page.get_by_role("button", name="Оформити замовлення").click()

    @property
    def summary(self):
        return self.page.locator("aside").first

    def summary_value(self, term: str) -> str:
        return self.summary.locator("dt", has_text=term).locator("xpath=following-sibling::dd[1]").inner_text()

    def total(self) -> int:
        return money(self.summary_value("Всього"))

    def is_valid(self, label: str) -> bool:
        return self.field(label).evaluate("el => el.validity.valid")


class OrderSuccessPage(BasePage):
    @property
    def heading(self):
        return self.page.get_by_role("heading", level=1)

    @property
    def order_number(self):
        return self.page.locator("p strong").filter(has_text=re.compile(r"^№"))

    def detail(self, term: str) -> str:
        return self.page.locator("dt", has_text=term).first.locator("xpath=following-sibling::dd[1]").inner_text()

    @property
    def items(self):
        return self.page.get_by_role("heading", name="Ваше замовлення").locator("xpath=..").locator("li")

    def wait(self):
        expect(self.page).to_have_url(re.compile(r"#/order-success"))
        expect(self.heading).to_have_text("Дякуємо за замовлення!")
        return self
