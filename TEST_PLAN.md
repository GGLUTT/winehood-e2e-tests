# WineHOOD Store: test plan and coverage

**Object:** WineHOOD Store, React SPA e-commerce for wine (https://gglutt.github.io/WineHood/).
**Scope:** age gate, catalog (filters, sorting, pagination), search, product page, cart, checkout and order confirmation, login and registration forms, navigation, newsletter form, responsive layout.
**Out of scope:** real payments and the real auth backend (mocked), performance and security testing.
**Approach:** test cases first (below), then automation in Python + Pytest + Playwright with the Page Object Model.
Negative paths and boundaries are covered as well as happy paths. Server answers are mocked with `page.route`, so no real accounts or orders are created.
**Environment:** Chromium, 1366×900 desktop (plus 375 and 768 px for layout checks), locale uk-UA, GitHub Actions on Ubuntu.

## Coverage

| Area | Checks | Automated tests |
|---|---|---|
| Age gate 18+ | shown on first visit, scroll locked, confirm is remembered after reload, reject leaves the store | 4 |
| Catalog | listing and counter, card content, filters (type, country, producer), AND / OR logic, discounts, price range and its boundaries, no-results state, reset, sorting by price, sorting kept after filtering | 21 |
| Search | by producer, country, wine type, case and extra spaces, no results, quick chips | 6 |
| Product page | opens from catalog, quantity selector min 1, add with quantity, correct product, unknown id, breadcrumb | 6 |
| Cart | empty state, badge, same product twice → quantity, subtotal = sum, +/− update subtotal, min quantity 1, remove, Ukrainian plural forms, close, wine type, continue shopping, reload | 14 |
| Checkout | items and totals, phone prefix, required fields, invalid e-mails, courier +99 ₴, courier needs city and address, full order with all details on confirmation, each payment method, cart emptied after order, empty cart, direct confirmation URL, invalid customer data | 18 |
| Login / registration | required fields, e-mail format, error clears on typing, password visibility, 401, 423 with server message, 500, success saves session, network failure, register rules (name, e-mail, password length, passwords match), exactly 8 chars boundary, 409, success payload | 18 |
| Navigation and layout | header menu, logo, footer info pages, 404, newsletter required and success, no horizontal scroll on phone / tablet / laptop for home, catalog, checkout | 22 |
| **Total** | | **109** (88 passing, 21 documenting 14 known bugs) |

## Test design techniques used
- **Equivalence partitioning and boundary values:** price range (inside, exact boundary), password length (7 vs 8 chars), quantity (never below 1), plural forms (1 / 2 / 5).
- **Decision table:** filter combinations (same section = OR, different sections = AND).
- **State transitions:** cart (empty → items → quantity changes → removed / ordered), age gate (new → confirmed → remembered).
- **Error guessing / negative testing:** invalid e-mails and phones, direct URLs to internal pages, unknown product id, server errors 401 / 409 / 423 / 500, network failure.
- **Data-driven tests:** `pytest.mark.parametrize` for filters, payment methods, validation rules and screen sizes.
