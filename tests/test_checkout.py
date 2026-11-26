"""Checkout and order confirmation."""
import re

import pytest
from playwright.sync_api import expect

from pages.checkout_page import CheckoutPage, OrderSuccessPage, money


@pytest.mark.smoke
def test_checkout_shows_cart_items_and_total(checkout_with_item):
    checkout, name, price = checkout_with_item
    expect(checkout.heading).to_have_text("Оформлення замовлення")
    expect(checkout.summary.locator("li")).to_have_count(1)
    expect(checkout.summary.locator("li").first).to_contain_text(name)
    assert money(checkout.summary_value("Товари")) == price
    assert checkout.summary_value("Доставка") == "Безкоштовно"
    assert checkout.total() == price


def test_phone_field_is_prefilled_with_country_code(checkout_with_item):
    checkout, *_ = checkout_with_item
    expect(checkout.field("Номер телефону")).to_have_value("+380")


def test_empty_required_fields_block_order(checkout_with_item):
    checkout, *_ = checkout_with_item
    checkout.submit()
    assert "#/checkout" in checkout.page.url
    assert checkout.is_valid("Ім'я") is False


@pytest.mark.parametrize("email", ["plainaddress", "user@", "@example.com"])
def test_invalid_email_blocks_order(checkout_with_item, email):
    checkout, *_ = checkout_with_item
    checkout.fill_customer(email=email)
    checkout.submit()
    assert "#/checkout" in checkout.page.url
    assert checkout.is_valid("Електронна пошта") is False


def test_courier_delivery_adds_99_to_total(checkout_with_item):
    checkout, _, price = checkout_with_item
    checkout.choose("Кур'єр Wine Hood")
    expect(checkout.summary.locator("dt", has_text="Доставка").locator("xpath=following-sibling::dd[1]")).to_have_text("99 ₴")
    assert checkout.total() == price + 99


def test_courier_delivery_requires_city_and_address(checkout_with_item):
    checkout, *_ = checkout_with_item
    checkout.fill_customer()
    checkout.choose("Кур'єр Wine Hood")
    checkout.submit()
    assert "#/checkout" in checkout.page.url
    assert checkout.is_valid("Місто") is False


@pytest.mark.smoke
def test_successful_order_shows_full_confirmation(checkout_with_item):
    checkout, name, price = checkout_with_item
    checkout.fill_customer(first="Олена", last="Коваль", phone="+380501112233", email="olena@example.com")
    checkout.choose("Кур'єр Wine Hood")
    checkout.field("Місто").fill("Київ")
    checkout.field("Адреса").fill("Хрещатик, 1")
    checkout.choose("Карткою онлайн")
    checkout.field("Коментар").fill("Подзвоніть заздалегідь")
    checkout.submit()

    success = OrderSuccessPage(checkout.page).wait()
    expect(success.order_number).to_have_text(re.compile(r"^№N\d{5}$"))
    recipient = success.detail("Отримувач")
    for value in ("Олена Коваль", "+380501112233", "olena@example.com"):
        assert value in recipient
    assert "Київ, Хрещатик, 1" in success.detail("Доставка")
    assert "Карткою" in success.detail("Оплата")
    assert success.detail("Коментар") == "Подзвоніть заздалегідь"
    expect(success.items).to_have_count(1)
    expect(success.items.first).to_contain_text(name)
    assert money(success.detail("До сплати")) == price + 99


@pytest.mark.parametrize("payment", ["Готівкою", "Карткою онлайн", "Безготівковий розрахунок"])
def test_order_with_each_payment_method(checkout_with_item, payment):
    checkout, *_ = checkout_with_item
    checkout.fill_customer()
    checkout.choose(payment)
    checkout.submit()
    success = OrderSuccessPage(checkout.page).wait()
    assert payment.split()[0] in success.detail("Оплата")


def test_cart_is_emptied_after_order(checkout_with_item):
    checkout, *_ = checkout_with_item
    checkout.fill_customer()
    checkout.submit()
    OrderSuccessPage(checkout.page).wait()
    expect(checkout.cart_badge).to_have_count(0)


def test_checkout_with_empty_cart_offers_catalog(page):
    CheckoutPage(page).open()
    expect(page.get_by_role("heading", level=1)).to_have_text("Ваш кошик порожній")
    page.get_by_role("link", name="Перейти до каталогу").first.click()
    page.wait_for_url("**#/catalog")


def test_confirmation_page_opened_directly_says_order_not_found(page):
    OrderSuccessPage(page).open("/order-success")
    expect(page.get_by_role("heading", level=1)).to_have_text("Замовлення не знайдено")


@pytest.mark.bug
@pytest.mark.parametrize(
    "first, phone, email",
    [("О", "+380501112233", "qa@example.com"), ("Олена", "123", "qa@example.com"), ("Олена", "+380501112233", "qa@x")],
    ids=["one-letter-name", "short-phone", "email-without-domain"],
)
@pytest.mark.xfail(reason="BUG-03: checkout accepts a 1-letter name, phone '123' and email without a domain")
def test_checkout_rejects_invalid_customer_data(checkout_with_item, first, phone, email):
    checkout, *_ = checkout_with_item
    checkout.fill_customer(first=first, phone=phone, email=email)
    checkout.submit()
    checkout.page.wait_for_timeout(1000)
    assert "#/order-success" not in checkout.page.url
