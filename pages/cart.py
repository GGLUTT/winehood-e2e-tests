import re

from playwright.sync_api import Page, expect


class Cart:
    """Slide-in shopping cart opened from the header."""

    def __init__(self, page: Page):
        self.page = page
        self.root = page.locator(".shopping-cart")

    def open(self):
        self.page.get_by_role("button", name="Кошик", exact=True).click()
        expect(self.root).to_be_visible()
        return self

    def close(self):
        self.root.locator(".close-cart").click()

    @property
    def items(self):
        return self.root.locator(".cart-item")

    @property
    def empty_message(self):
        return self.root.locator(".empty-cart")

    def quantity(self, index: int = 0) -> int:
        return int(self.items.nth(index).locator(".quantity-control span").inner_text())

    def plus(self, index: int = 0):
        self.items.nth(index).locator(".quantity-control button").nth(1).click()

    def minus(self, index: int = 0):
        self.items.nth(index).locator(".quantity-control button").nth(0).click()

    def remove(self, index: int = 0):
        self.items.nth(index).locator(".remove-item").click()

    def subtotal(self) -> int:
        return int(re.sub(r"\D", "", self.root.locator(".subtotal-amount").inner_text()))

    @property
    def items_count_label(self):
        return self.root.locator(".item-count")

    def item_type(self, index: int = 0) -> str:
        return self.items.nth(index).locator(".item-type").inner_text()

    def go_to_checkout(self):
        self.root.get_by_role("button", name="ПЕРЕЙТИ ДО ОФОРМЛЕННЯ").click()

    def continue_shopping(self):
        self.root.get_by_role("button", name="ПРОДОВЖИТИ ПОКУПКИ").click()
