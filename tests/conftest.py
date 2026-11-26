import re

import pytest
from playwright.sync_api import Page, expect

from pages.cart import Cart
from pages.catalog_page import CatalogPage
from pages.checkout_page import CheckoutPage


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "locale": "uk-UA", "viewport": {"width": 1366, "height": 900}}


@pytest.fixture
def page(page: Page) -> Page:
    """Page for an adult visitor: the 18+ age gate is already confirmed."""
    page.set_default_timeout(15_000)
    page.add_init_script("window.localStorage.setItem('ageVerified', 'true')")
    return page


@pytest.fixture
def new_visitor(context) -> Page:
    """Clean page of a first-time visitor (age gate not confirmed yet)."""
    p = context.new_page()
    p.set_default_timeout(15_000)
    return p


@pytest.fixture
def catalog(page) -> CatalogPage:
    return CatalogPage(page).open()


@pytest.fixture
def cart(page) -> Cart:
    return Cart(page)


@pytest.fixture
def checkout_with_item(catalog, cart):
    """The cart lives in memory, so the item is added through the UI, then the user goes to checkout."""
    name, price = catalog.card_name(0), catalog.card_price(0)
    catalog.add_to_cart(0)
    cart.open().go_to_checkout()
    checkout = CheckoutPage(catalog.page)
    expect(checkout.page).to_have_url(re.compile(r"#/checkout$"))
    return checkout, name, price
