"""Product details page."""
import re

import pytest
from playwright.sync_api import expect

from pages.product_page import ProductPage


def test_clicking_card_opens_product_page(catalog):
    catalog.open_product(0)
    catalog.page.wait_for_url(re.compile(r"#/product/\d+$"))
    expect(ProductPage(catalog.page).title).to_be_visible()


def test_quantity_selector_increments_and_never_goes_below_one(catalog):
    catalog.open_product(0)
    product = ProductPage(catalog.page)
    expect(product.quantity).to_have_text("1")
    product.minus()
    expect(product.quantity).to_have_text("1")
    product.plus()
    product.plus()
    expect(product.quantity).to_have_text("3")
    product.minus()
    expect(product.quantity).to_have_text("2")


def test_add_to_cart_with_selected_quantity(catalog, cart):
    catalog.open_product(0)
    product = ProductPage(catalog.page)
    product.plus()
    product.plus()
    product.add_to_cart()
    expect(product.cart_badge).to_have_text("3")
    cart.open()
    assert cart.quantity(0) == 3
    assert cart.subtotal() == product.price_value() * 3


@pytest.mark.bug
@pytest.mark.xfail(reason="BUG-01: every product page shows the same hard-coded wine (Santa Julia, 480 ₴)")
def test_product_page_shows_the_clicked_product(catalog):
    name, price = catalog.card_name(0), catalog.card_price(0)
    catalog.open_product(0)
    product = ProductPage(catalog.page)
    expect(product.title).to_contain_text(name)
    assert product.price_value() == price


@pytest.mark.bug
@pytest.mark.xfail(reason="BUG-02: a non-existing product id opens a product page instead of 404")
def test_unknown_product_id_shows_not_found(page):
    ProductPage(page).open("/product/999999")
    expect(page.locator(".not-found-title")).to_be_visible()


@pytest.mark.bug
@pytest.mark.xfail(reason="BUG-12: product breadcrumb shows English 'Product' and a raw id instead of the wine name")
def test_product_breadcrumb_shows_catalog_and_wine_name(catalog):
    name = catalog.card_name(0)
    catalog.open_product(0)
    crumbs = catalog.page.locator("nav").filter(has=catalog.page.get_by_role("link", name="Головна")).last
    expect(crumbs).to_contain_text("Каталог")
    expect(crumbs).to_contain_text(name)
