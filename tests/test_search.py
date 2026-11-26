"""Header search: free text over name, producer, country and wine type."""
import re

import pytest
from playwright.sync_api import expect

from pages.base import BasePage
from pages.catalog_page import CatalogPage


def search(page, query: str):
    BasePage(page).open()
    page.get_by_role("button", name="Пошук").click()
    box = page.locator(".search-input")
    expect(box).to_be_visible()
    box.fill(query)
    box.press("Enter")
    expect(page).to_have_url(re.compile(r"#/catalog\?q="))
    return CatalogPage(page)


@pytest.mark.smoke
def test_search_by_producer(page):
    catalog = search(page, "Penfolds")
    expect(catalog.cards).to_have_count(4)
    assert set(catalog.names()) == {"Penfolds Bin 60A"}


@pytest.mark.parametrize(
    "query, expected",
    [("франція", {"Domaine Desvignes", "Whispering Angel"}), ("Червоне", {"Penfolds Bin 60A"})],
    ids=["country-lowercase", "wine-type"],
)
def test_search_by_country_and_type(page, query, expected):
    catalog = search(page, query)
    expect(catalog.cards.first).to_be_visible()
    assert set(catalog.names()) == expected


def test_search_ignores_case_and_extra_spaces(page):
    catalog = search(page, "  cLoUdY  ")
    expect(catalog.cards).to_have_count(1)
    assert catalog.names() == ["Cloudy Bay"]


def test_search_without_results(page):
    catalog = search(page, "zzzz")
    expect(catalog.cards).to_have_count(0)
    expect(catalog.no_results).to_contain_text("За вашим запитом товарів не знайдено")


def test_quick_chip_fills_search_box(page):
    BasePage(page).open()
    page.get_by_role("button", name="Пошук").click()
    page.locator(".search-chip", has_text="Рожеве").click()
    expect(page.locator(".search-input")).to_have_value("Рожеве")
