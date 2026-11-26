import re

from .base import BasePage


class ProductPage(BasePage):
    @property
    def title(self):
        return self.page.locator("h1").first

    @property
    def price(self):
        return self.page.locator(".price").first

    @property
    def quantity(self):
        return self.page.locator(".quantity-values")

    def plus(self):
        self.page.locator(".quantity-controls .quantity-btn").nth(1).click()

    def minus(self):
        self.page.locator(".quantity-controls .quantity-btn").nth(0).click()

    def add_to_cart(self):
        self.page.locator(".add-to-cart-new").click()
        self.page.wait_for_timeout(300)

    def price_value(self) -> int:
        return int(re.sub(r"\D", "", self.price.inner_text()))
