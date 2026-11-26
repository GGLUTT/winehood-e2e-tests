# WineHOOD Store: bug reports

Found while testing the live build at https://gglutt.github.io/WineHood/ (Chrome, desktop 1366×900, uk-UA).
Every bug has an automated test marked `@pytest.mark.bug` + `xfail(strict=True)`: the suite stays green while the bug exists,
and the test turns red (XPASS) as soon as the bug is fixed, so the fix gets noticed and the marker removed.

| ID | Title | Severity | Priority | Area | Test |
|---|---|---|---|---|---|
| BUG-01 | Product page always shows the same wine, not the one clicked | Critical | High | Product | `test_product.py::test_product_page_shows_the_clicked_product` |
| BUG-02 | Non-existing product id opens a product page instead of 404 | Major | Medium | Product | `test_product.py::test_unknown_product_id_shows_not_found` |
| BUG-03 | Checkout accepts a 1-letter name, phone "123" and e-mail without a domain | Major | High | Checkout | `test_checkout.py::test_checkout_rejects_invalid_customer_data` |
| BUG-04 | Cart shows "Червоне сухе вино" for every product | Major | Medium | Cart | `test_cart.py::test_cart_shows_correct_wine_type` |
| BUG-05 | "ПРОДОВЖИТИ ПОКУПКИ" button in the cart does nothing | Major | Medium | Cart | `test_cart.py::test_continue_shopping_closes_cart` |
| BUG-06 | Cart is lost after a page reload | Major | Medium | Cart | `test_cart.py::test_cart_survives_page_reload` |
| BUG-07 | Pagination shows 103 pages for 9 products; "НАСТУПНА" opens empty pages | Major | Medium | Catalog | `test_catalog.py::test_pagination_matches_number_of_products` |
| BUG-08 | "Скинути фільтри" sets min price to 500 instead of the default 300 | Minor | Low | Catalog | `test_catalog.py::test_reset_restores_default_price_range` |
| BUG-09 | Search inside a filter (Країна, Виробник) loses focus after the first letter | Major | Medium | Catalog | `test_catalog.py::test_country_search_keeps_focus_while_typing` |
| BUG-10 | Product counter uses a wrong plural form: "1 Товарів", "3 Товарів" | Minor | Low | Catalog | `test_catalog.py::test_product_counter_uses_correct_plural_form` |
| BUG-11 | Login / registration show a raw "Failed to fetch" error; production backend is unreachable | Critical | High | Auth | `test_auth.py::test_login_network_failure_shows_friendly_message` |
| BUG-12 | Product breadcrumb shows English "Product" and a raw id | Minor | Low | Product | `test_product.py::test_product_breadcrumb_shows_catalog_and_wine_name` |
| BUG-13 | Login divider "ОR" uses a Cyrillic "О" (register page has Latin "OR") | Trivial | Low | Auth | `test_auth.py::test_login_divider_text` |
| BUG-14 | All footer info links (help, returns, delivery, privacy, terms) open the 404 page | Major | Medium | Navigation | `test_navigation.py::test_footer_info_pages_exist` |

---

### BUG-01: Product page always shows the same wine, not the one clicked
**Severity:** Critical · **Priority:** High
**Steps**
1. Open `#/catalog`.
2. Click the card "Cloudy Bay" (2850 ₴).

**Expected:** the page of Cloudy Bay, price 2850 ₴.
**Actual:** URL is `#/product/4`, but the page shows "Santa Julia Reserva Malbec Valle de Uco", 480 ₴. Any card and any id show the same wine, so the user can add a different product at a different price to the cart.
**Likely cause:** the product page uses hard-coded data and ignores the `productId` route parameter.

### BUG-02: Non-existing product id opens a product page
**Steps:** open `#/product/999999`.
**Expected:** 404 page ("Здається, ми щось пролили...").
**Actual:** product page of Santa Julia is shown.

### BUG-03: Checkout accepts invalid customer data
**Steps**
1. Add any wine to the cart, open checkout.
2. Fill Ім'я = `О`, Прізвище = `К`, Телефон = `123`, Email = `qa@x`.
3. Click "Оформити замовлення".

**Expected:** validation messages, the order is not placed (name 2+ letters, phone in `+380XXXXXXXXX` format, e-mail with a domain zone).
**Actual:** order is placed, confirmation page shows "Дякуємо за замовлення!". The shop can't contact such a customer.

### BUG-04: Cart shows "Червоне сухе вино" for every product
**Steps:** add "Cloudy Bay" (catalog shows "Біле вино") to the cart, open the cart.
**Expected:** "Біле вино".
**Actual:** "Червоне сухе вино". The checkout summary shows the correct type, so the two screens contradict each other.

### BUG-05: "ПРОДОВЖИТИ ПОКУПКИ" does nothing
**Steps:** add any wine, open the cart, click "ПРОДОВЖИТИ ПОКУПКИ".
**Expected:** the cart closes and the user stays in the catalog.
**Actual:** nothing happens, the cart stays open.

### BUG-06: Cart is lost after a page reload
**Steps:** add any wine (badge shows 1), press F5.
**Expected:** the cart still has 1 item.
**Actual:** the cart is empty. The cart is kept only in memory (nothing in localStorage).

### BUG-07: Pagination shows 103 pages for 9 products
**Steps:** open `#/catalog`, look at the pagination, click "НАСТУПНА".
**Expected:** "Сторінка 1 з 1", "НАСТУПНА" disabled.
**Actual:** "з 103"; "НАСТУПНА" opens page 2 with no products and the empty-result message is not shown.

### BUG-08: Reset filters sets wrong minimum price
**Steps:** open the catalog (min price = 300), set price 1000–5000, click "Скинути фільтри".
**Expected:** min price 300 (the initial default).
**Actual:** min price 500; products priced 300–499 would be hidden after a reset.

### BUG-09: Filter search loses focus after the first letter
**Steps:** in the "Країна" filter click the search box and type `Фра`.
**Expected:** the box contains `Фра`, the list shows Франція.
**Actual:** the box contains only `Ф`; the input loses focus after every key, so the user has to click again for each letter.
**Likely cause:** the filter section component is declared inside the catalog component and is re-created on each render.

### BUG-10: Wrong plural form in the product counter
**Steps:** filter by "Рожеве" (1 product) or "Червоне" (3 products).
**Expected:** "1 товар", "3 товари".
**Actual:** "1 Товарів", "3 Товарів". (The cart already uses correct forms: "1 товар", "2 товари", "5 товарів".)

### BUG-11: Login and registration do not work in production
**Steps:** open `#/login`, enter a valid e-mail and password, click "УВІЙТИ".
**Expected:** the user is logged in, or gets a clear message if the server is unavailable.
**Actual:** the request goes to a placeholder host and fails; the user sees the raw browser error "Failed to fetch". Same on `#/register`.
**Note:** the client-side logic is correct: with a mocked backend the tests confirm the 401, 409, 500 and success paths.

### BUG-12: Product breadcrumb is wrong
**Steps:** open any product from the catalog.
**Expected:** "Головна › Каталог › <wine name>".
**Actual:** "Головна › Product › 4" (English word and raw id in a Ukrainian UI).

### BUG-13: "ОR" on the login page uses a Cyrillic letter
**Steps:** open `#/login`, look at the divider above the Google button.
**Expected:** "OR" (or "АБО") like on the register page.
**Actual:** "ОR" with a Cyrillic "О": looks the same but breaks search/translation and is inconsistent.

### BUG-14: Footer info pages are missing
**Steps:** scroll to the footer, click "Довідковий центр" (also "Політика повернення", "Інформація про доставку", "Політика конфіденційності", "Умови обслуговування").
**Expected:** the corresponding information page.
**Actual:** 404 page "Здається, ми щось пролили...". Delivery and returns info matter for a store that sells alcohol online.
