import os

from playwright.sync_api import Page, expect

BASE_URL = os.getenv("BASE_URL", "https://gglutt.github.io/WineHood/").rstrip("/") + "/"


class BasePage:
    """Common actions for every page of the SPA (hash routing: BASE_URL#/route)."""

    route = ""

    def __init__(self, page: Page):
        self.page = page

    def open(self, route: str | None = None):
        route = self.route if route is None else route
        self.page.goto(BASE_URL + (f"#{route}" if route else ""))
        expect(self.page.locator("header.header")).to_be_visible()
        return self

    @property
    def url_route(self) -> str:
        return self.page.url.split("#", 1)[1] if "#" in self.page.url else "/"

    # header
    @property
    def cart_button(self):
        return self.page.get_by_role("button", name="Кошик", exact=True)

    @property
    def cart_badge(self):
        return self.page.locator(".cart-badge")

    def nav_link(self, text: str):
        return self.page.locator(".nav-menu").get_by_role("link", name=text, exact=True)
