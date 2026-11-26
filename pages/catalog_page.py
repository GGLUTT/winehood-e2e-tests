import re

from playwright.sync_api import expect

from .base import BasePage


def _digits(text: str) -> int:
    return int(re.sub(r"\D", "", text))


class CatalogPage(BasePage):
    route = "/catalog"

    def open(self, route=None):
        super().open(route)
        expect(self.cards.first).to_be_visible()
        return self

    @property
    def cards(self):
        return self.page.locator(".wine-card")

    @property
    def product_count(self):
        return self.page.locator(".product-count")

    @property
    def no_results(self):
        return self.page.locator(".no-products-message")

    @property
    def price_inputs(self):
        return self.page.locator(".price-input")

    @property
    def pagination(self):
        return self.page.locator(".pagination")

    def names(self) -> list[str]:
        return self.page.locator(".wine-card .wine-name").all_inner_texts()

    def prices(self) -> list[int]:
        return [_digits(t) for t in self.page.locator(".wine-card .wine-price").all_inner_texts()]

    def card_price(self, index: int) -> int:
        return _digits(self.cards.nth(index).locator(".wine-price").inner_text())

    def card_name(self, index: int) -> str:
        return self.cards.nth(index).locator(".wine-name").inner_text()

    def filter_section(self, title: str):
        return self.page.locator(".filter-section").filter(
            has=self.page.locator(".filter-title", has_text=re.compile(rf"^{re.escape(title)}$"))
        )

    def toggle_filter(self, section: str, option: str):
        label = self.filter_section(section).locator("label.filter-option").filter(
            has_text=re.compile(rf"^\s*{re.escape(option)}\s*$")
        )
        label.locator("input").click()

    def only_discounts(self):
        self.page.locator("label.filter-option", has_text="Показати тільки знижки").locator("input").click()

    def set_price(self, minimum: int | None = None, maximum: int | None = None):
        if minimum is not None:
            self.price_inputs.nth(0).fill(str(minimum))
        if maximum is not None:
            self.price_inputs.nth(1).fill(str(maximum))

    def sort_by(self, option: str):
        self.page.locator(".sort-select").select_option(option)

    def reset_filters(self):
        self.page.get_by_role("button", name="Скинути фільтри").click()

    def add_to_cart(self, index: int):
        self.cards.nth(index).locator(".add-to-cart").click()
        # the app ignores repeated adds of the same product within 1 s (debounce)
        self.page.wait_for_timeout(1100)

    def open_product(self, index: int):
        self.cards.nth(index).locator(".wine-card-content").click()
