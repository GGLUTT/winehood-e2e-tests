"""Header and footer navigation, 404 page, newsletter form, responsive layout."""
import re

import pytest
from playwright.sync_api import expect

from pages.base import BasePage


@pytest.mark.smoke
@pytest.mark.parametrize(
    "link, route, heading",
    [
        ("Каталог", "/catalog", None),
        ("Акції", "/promotions", "Акції та спеціальні пропозиції"),
        ("Блог", "/blog", "Наш блог"),
        ("Про нас", "/about", "Про нас"),
    ],
)
def test_header_menu_links(page, link, route, heading):
    home = BasePage(page).open()
    home.nav_link(link).click()
    expect(page).to_have_url(re.compile(re.escape(f"#{route}") + "$"))
    expect(page.get_by_role("heading").first).to_be_visible()
    expect(page.locator(".not-found-title")).to_have_count(0)
    if heading:
        expect(page.get_by_role("heading", level=1)).to_have_text(re.compile(heading, re.I))


def test_logo_returns_to_home(page):
    BasePage(page).open("/catalog")
    page.get_by_role("link", name="Wine Hood — на головну").click()
    expect(page).to_have_url(re.compile(r"#/$"))


@pytest.mark.bug
@pytest.mark.parametrize("route", ["/help", "/returns", "/delivery", "/privacy", "/terms"])
@pytest.mark.xfail(reason="BUG-14: all footer info links (help, returns, delivery, privacy, terms) lead to the 404 page")
def test_footer_info_pages_exist(page, route):
    BasePage(page).open()
    page.locator(f"footer a[href='#{route}']").click()
    expect(page).to_have_url(re.compile(re.escape(f"#{route}") + "$"))
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)  # let the router render the new route before checking for 404
    assert page.locator(".not-found-title").count() == 0, f"#{route} shows the 404 page"


def test_unknown_route_shows_404(page):
    BasePage(page).open("/no-such-page")
    expect(page.locator(".not-found-title")).to_have_text(re.compile("Здається, ми щось пролили", re.I))


def test_newsletter_requires_email(page):
    BasePage(page).open()
    page.get_by_role("button", name="Підписатися").click()
    box = page.get_by_role("textbox", name="Електронна адреса")
    assert box.evaluate("el => el.validity.valid") is False
    expect(page.locator("footer")).not_to_contain_text("Дякуємо!")


def test_newsletter_subscription_confirms(page):
    BasePage(page).open()
    page.get_by_role("textbox", name="Електронна адреса").fill("qa@example.com")
    page.get_by_role("button", name="Підписатися").click()
    expect(page.locator("footer")).to_contain_text("Дякуємо! Промокод уже летить на вашу пошту.")


@pytest.mark.parametrize("width, height", [(375, 812), (768, 1024), (1366, 900)], ids=["phone", "tablet", "laptop"])
@pytest.mark.parametrize("route", ["", "/catalog", "/checkout"], ids=["home", "catalog", "checkout"])
def test_no_horizontal_scroll(page, route, width, height):
    page.set_viewport_size({"width": width, "height": height})
    BasePage(page).open(route)
    page.wait_for_timeout(500)
    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    assert overflow <= 1, f"page is {overflow}px wider than a {width}px screen"
