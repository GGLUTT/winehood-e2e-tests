"""Shopping cart: add, quantity, remove, totals."""
import pytest
from playwright.sync_api import expect


@pytest.mark.smoke
def test_empty_cart_message(catalog, cart):
    cart.open()
    expect(cart.empty_message).to_have_text("Ваш кошик порожній")
    expect(catalog.cart_badge).to_have_count(0)


@pytest.mark.smoke
def test_adding_product_updates_badge_and_cart(catalog, cart):
    name, price = catalog.card_name(0), catalog.card_price(0)
    catalog.add_to_cart(0)
    expect(catalog.cart_badge).to_have_text("1")
    cart.open()
    expect(cart.items).to_have_count(1)
    expect(cart.items.first.locator(".item-name")).to_have_text(name)
    assert cart.subtotal() == price


def test_adding_same_product_twice_increases_quantity_not_rows(catalog, cart):
    catalog.add_to_cart(0)
    catalog.add_to_cart(0)
    expect(catalog.cart_badge).to_have_text("2")
    cart.open()
    expect(cart.items).to_have_count(1)
    assert cart.quantity(0) == 2


def test_subtotal_is_sum_of_all_items(catalog, cart):
    prices = [catalog.card_price(0), catalog.card_price(1)]
    catalog.add_to_cart(0)
    catalog.add_to_cart(1)
    cart.open()
    expect(cart.items).to_have_count(2)
    assert cart.subtotal() == sum(prices)


def test_quantity_buttons_update_subtotal(catalog, cart):
    price = catalog.card_price(0)
    catalog.add_to_cart(0)
    cart.open()
    cart.plus()
    cart.plus()
    assert cart.quantity() == 3
    assert cart.subtotal() == price * 3
    cart.minus()
    assert cart.subtotal() == price * 2


def test_quantity_cannot_go_below_one(catalog, cart):
    catalog.add_to_cart(0)
    cart.open()
    cart.minus()
    assert cart.quantity() == 1


def test_removing_last_item_empties_cart(catalog, cart):
    catalog.add_to_cart(0)
    cart.open()
    cart.remove()
    expect(cart.empty_message).to_be_visible()
    expect(catalog.cart_badge).to_have_count(0)


@pytest.mark.parametrize("clicks, label", [(0, "(1 товар)"), (1, "(2 товари)"), (4, "(5 товарів)")])
def test_ukrainian_plural_form_of_items_count(catalog, cart, clicks, label):
    catalog.add_to_cart(0)
    cart.open()
    for _ in range(clicks):
        cart.plus()
    expect(cart.items_count_label).to_have_text(label)


def test_cart_closes_with_cross(catalog, cart):
    cart.open()
    cart.close()
    expect(cart.root).to_be_hidden()


@pytest.mark.bug
@pytest.mark.xfail(reason="BUG-04: cart shows 'Червоне сухе вино' for every product, also for white wine")
def test_cart_shows_correct_wine_type(catalog, cart):
    wine_type = catalog.cards.nth(0).locator(".wine-type").inner_text()  # 'Біле вино'
    catalog.add_to_cart(0)
    cart.open()
    assert wine_type.split()[0] in cart.item_type(0)


@pytest.mark.bug
@pytest.mark.xfail(reason="BUG-05: 'ПРОДОВЖИТИ ПОКУПКИ' button has no action, the cart stays open")
def test_continue_shopping_closes_cart(catalog, cart):
    catalog.add_to_cart(0)
    cart.open()
    cart.continue_shopping()
    expect(cart.root).to_be_hidden(timeout=3000)


@pytest.mark.bug
@pytest.mark.xfail(reason="BUG-06: the cart is lost after a page reload")
def test_cart_survives_page_reload(catalog):
    catalog.add_to_cart(0)
    expect(catalog.cart_badge).to_have_text("1")
    catalog.page.reload()
    expect(catalog.page.locator("header.header")).to_be_visible()
    expect(catalog.cart_badge).to_have_text("1", timeout=3000)
