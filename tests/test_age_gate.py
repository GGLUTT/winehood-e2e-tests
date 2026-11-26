"""18+ age verification (required by law for an alcohol store)."""
import re

import pytest
from playwright.sync_api import expect

from pages.base import BASE_URL

MODAL = ".age-verification-modal"


@pytest.mark.smoke
def test_age_gate_is_shown_to_first_time_visitor(new_visitor):
    new_visitor.goto(BASE_URL)
    expect(new_visitor.locator(MODAL)).to_be_visible()
    expect(new_visitor.locator(MODAL)).to_contain_text("ХМ, А ВАМ ВЖЕ Є 18?")


def test_page_scroll_is_locked_while_age_gate_is_open(new_visitor):
    new_visitor.goto(BASE_URL)
    expect(new_visitor.locator(MODAL)).to_be_visible()
    assert new_visitor.evaluate("getComputedStyle(document.body).overflow") == "hidden"


def test_confirming_age_hides_gate_and_is_remembered(new_visitor):
    new_visitor.goto(BASE_URL)
    new_visitor.get_by_role("button", name="ТАК, МЕНІ ВЖЕ 18").click()
    expect(new_visitor.locator(MODAL)).to_be_hidden()
    assert new_visitor.evaluate("localStorage.getItem('ageVerified')") == "true"

    new_visitor.reload()
    expect(new_visitor.locator("header.header")).to_be_visible()
    expect(new_visitor.locator(MODAL)).to_be_hidden()


def test_rejecting_age_sends_user_away_from_store(new_visitor):
    # the external page is answered locally so the test does not depend on google.com
    new_visitor.route("https://www.google.com/**", lambda route: route.fulfill(body="left the store"))
    new_visitor.goto(BASE_URL)
    new_visitor.get_by_role("button", name="НІ, МЕНІ ЩЕ НЕМАЄ 18").click()
    new_visitor.wait_for_url(re.compile(r"google\.com"))
    assert new_visitor.evaluate("localStorage.getItem('ageVerified')") is None
