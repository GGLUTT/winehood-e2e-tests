"""Catalog: listing, filters, sorting, pagination."""
import pytest
from playwright.sync_api import expect

ALL_PRODUCTS = 9


@pytest.mark.smoke
def test_catalog_lists_all_products_with_counter(catalog):
    expect(catalog.cards).to_have_count(ALL_PRODUCTS)
    expect(catalog.product_count).to_have_text(f"{ALL_PRODUCTS} Товарів")


def test_every_card_has_name_price_and_add_button(catalog):
    for i in range(catalog.cards.count()):
        card = catalog.cards.nth(i)
        expect(card.locator(".wine-name")).not_to_be_empty()
        expect(card.locator(".wine-price")).to_contain_text("₴")
        expect(card.locator(".add-to-cart")).to_have_text("До кошика")


@pytest.mark.parametrize(
    "section, option, expected_names",
    [
        ("Тип вина", "Рожеве", ["Whispering Angel"]),
        ("Країна", "Іспанія", ["Lou Rosé"]),
        ("Виробник", "Cloudy Bay", ["Cloudy Bay"]),
    ],
)
def test_single_filter(catalog, section, option, expected_names):
    catalog.toggle_filter(section, option)
    expect(catalog.cards).to_have_count(len(expected_names))
    assert catalog.names() == expected_names
    expect(catalog.product_count).to_have_text(f"{len(expected_names)} Товарів")


def test_filters_in_different_sections_are_combined_with_and(catalog):
    catalog.toggle_filter("Тип вина", "Біле")
    catalog.toggle_filter("Країна", "Франція")
    expect(catalog.cards).to_have_count(1)
    assert catalog.names() == ["Domaine Desvignes"]


def test_options_in_one_section_are_combined_with_or(catalog):
    catalog.toggle_filter("Тип вина", "Рожеве")
    catalog.toggle_filter("Тип вина", "Червоне")
    expect(catalog.cards).to_have_count(4)  # 1 rosé + 3 red


def test_unchecking_filter_restores_list(catalog):
    catalog.toggle_filter("Тип вина", "Рожеве")
    expect(catalog.cards).to_have_count(1)
    catalog.toggle_filter("Тип вина", "Рожеве")
    expect(catalog.cards).to_have_count(ALL_PRODUCTS)


def test_discount_filter_shows_only_items_on_sale(catalog):
    catalog.only_discounts()
    expect(catalog.cards).to_have_count(3)
    for i in range(3):
        expect(catalog.cards.nth(i).locator(".sale-badge")).to_have_text("Знижка")


def test_price_range_filter_keeps_only_prices_inside_range(catalog):
    catalog.set_price(2000, 3000)
    expect(catalog.cards).to_have_count(3)
    assert all(2000 <= p <= 3000 for p in catalog.prices())


def test_price_range_boundaries_are_inclusive(catalog):
    catalog.set_price(2850, 2850)
    expect(catalog.cards).to_have_count(1)
    assert catalog.prices() == [2850]


def test_no_results_message_when_nothing_matches(catalog):
    catalog.set_price(1, 100)
    expect(catalog.cards).to_have_count(0)
    expect(catalog.no_results).to_contain_text("За вашим запитом товарів не знайдено")
    expect(catalog.product_count).to_have_text("0 Товарів")
    expect(catalog.pagination).to_have_count(0)


def test_reset_button_clears_all_filters(catalog):
    catalog.toggle_filter("Тип вина", "Рожеве")
    catalog.only_discounts()
    expect(catalog.cards).to_have_count(0)
    catalog.reset_filters()
    expect(catalog.cards).to_have_count(ALL_PRODUCTS)


@pytest.mark.parametrize(
    "option, reverse",
    [("За збільшенням ціни", False), ("За зменшенням ціни", True)],
)
def test_sort_by_price(catalog, option, reverse):
    catalog.sort_by(option)
    prices = catalog.prices()
    assert prices == sorted(prices, reverse=reverse)


def test_sorting_is_kept_after_filtering(catalog):
    catalog.sort_by("За збільшенням ціни")
    catalog.toggle_filter("Тип вина", "Біле")
    prices = catalog.prices()
    assert len(prices) == 5
    assert prices == sorted(prices)


@pytest.mark.bug
@pytest.mark.xfail(reason="BUG-08: 'Скинути фільтри' sets min price to 500 instead of the default 300")
def test_reset_restores_default_price_range(catalog):
    expect(catalog.price_inputs.nth(0)).to_have_value("300")
    catalog.set_price(1000, 5000)
    catalog.reset_filters()
    expect(catalog.price_inputs.nth(0)).to_have_value("300")


@pytest.mark.bug
@pytest.mark.xfail(reason="BUG-07: pagination is hard-coded to 103 pages for 9 products")
def test_pagination_matches_number_of_products(catalog):
    expect(catalog.pagination).to_contain_text("з 1")
    expect(catalog.pagination.get_by_role("button", name="НАСТУПНА")).to_be_disabled()


@pytest.mark.bug
@pytest.mark.xfail(reason="BUG-09: search inside a filter loses focus after the first typed letter")
def test_country_search_keeps_focus_while_typing(catalog):
    search = catalog.filter_section("Країна").locator(".filter-search-input")
    search.click()
    catalog.page.keyboard.type("Фра", delay=80)
    expect(catalog.filter_section("Країна").locator(".filter-search-input")).to_have_value("Фра")


@pytest.mark.bug
@pytest.mark.parametrize("option, expected", [("Рожеве", "1 товар"), ("Червоне", "3 товари")])
@pytest.mark.xfail(reason="BUG-10: product counter always says 'Товарів' (1 Товарів, 3 Товарів)")
def test_product_counter_uses_correct_plural_form(catalog, option, expected):
    catalog.toggle_filter("Тип вина", option)
    expect(catalog.product_count).to_have_text(expected, ignore_case=True)
