# WineHOOD Store: e2e test automation (Python + Pytest + Playwright)

Automated UI tests and QA documentation for [WineHOOD Store](https://gglutt.github.io/WineHood/), an e-commerce web app for wine (React SPA).

- **109 automated tests** across age gate, catalog, search, product page, cart, checkout, auth forms and navigation
- **14 bugs found and documented** with steps to reproduce: [BUG_REPORTS.md](BUG_REPORTS.md)
- **Test plan and coverage:** [TEST_PLAN.md](TEST_PLAN.md)
- Runs in **GitHub Actions** on every push, manually and weekly; failed tests save screenshots

## Stack and approach
- Python 3.12, Pytest, Playwright (pytest-playwright), Chromium
- **Page Object Model** (`pages/`): one class per page or widget, tests describe behaviour only
- **Fixtures** for state: an adult visitor (age gate confirmed), a first-time visitor, a cart with an item ready for checkout
- **Network mocking** with `page.route`: login and registration are tested against mocked 200 / 401 / 409 / 423 / 500 answers and a network failure; the tests also check the request payload
- **Known bugs as tests:** each bug is an `xfail(strict=True)` test marked `bug`. The run stays green while the bug exists and turns red when it is fixed.
- Data-driven tests (`parametrize`), smoke marker for a fast critical-path run

## Structure
```
pages/        Page Objects: base, catalog, product, cart, checkout + order success, login / register
tests/        test_age_gate, test_catalog, test_search, test_product, test_cart, test_checkout, test_auth, test_navigation
BUG_REPORTS.md  14 defects: severity, priority, steps, expected / actual
TEST_PLAN.md    scope, approach, coverage per area, test design techniques
```

## Run
```bash
pip install -r requirements.txt
playwright install chromium

pytest                      # everything (109 tests)
pytest -m smoke             # critical path only
pytest -m bug               # only the tests that document known bugs
pytest --headed --slowmo 300  # watch the browser
BASE_URL=http://localhost:3000/ pytest   # run against a local build
```
