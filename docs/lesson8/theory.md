# Урок 8 — Статические таблицы в Playwright

## Что такое таблица в HTML

Классическая таблица в HTML — это структура из вложенных тегов:

```html
<table>
  <thead>
    <tr>
      <th>Title</th>
      <th>Author</th>
      <th>Price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Learn Java</td>
      <td>Mukesh</td>
      <td>500</td>
    </tr>
    <tr>
      <td>Master Selenium</td>
      <td>John</td>
      <td>700</td>
    </tr>
  </tbody>
</table>
```

Ключевые элементы:

| Тег       | Что значит                            |
|-----------|---------------------------------------|
| `<table>` | Контейнер всей таблицы                |
| `<thead>` | Заголовок (необязателен)              |
| `<tbody>` | Тело — строки данных                  |
| `<tr>`    | Table row — одна строка               |
| `<th>`    | Ячейка-заголовок (внутри `<thead>`)   |
| `<td>`    | Обычная ячейка (внутри `<tr>` в tbody)|

> ⚠️ Не каждая "таблица" на сайте — это `<table>`. Angular/React-приложения
> часто строят таблицы из `<div>` с `role="row"`, `role="cell"`, или вообще
> через CSS Grid. Сначала открой DevTools и **посмотри**, что у тебя в DOM.

---

## Современные альтернативы `<table>`

Многие SPA рендерят таблицу как набор div'ов:

```html
<div role="table" aria-label="Cart items">
  <div role="row">
    <div role="cell">Hammer</div>
    <div role="cell">$15.99</div>
    <div role="cell">2</div>
  </div>
</div>
```

Или вообще без ARIA, на чистом CSS Grid:

```html
<div class="cart-list">
  <div class="cart-item">
    <span>Hammer</span>
    <span>$15.99</span>
    <span>2</span>
  </div>
</div>
```

С точки зрения тестов это **всё ещё таблица** — есть строки и колонки. Просто
локаторы будут другими:

| HTML-таблица      | Div-таблица с ARIA               | Div-таблица без ARIA            |
|-------------------|----------------------------------|---------------------------------|
| `table`           | `[role='table']`                 | `.cart-list` / `[data-test=...]`|
| `tr`              | `[role='row']`                   | `.cart-item` / row-локатор сайта|
| `td` / `th`       | `[role='cell']`                  | `span` / column-локатор         |

Главное — **выбрать стабильный селектор для строки** и считать всё относительно него.

---

## Локаторы для таблицы

### 1. Найти таблицу

```python
table = page.locator("table[data-test='cart-table']")
expect(table).to_be_visible()
```

Используй `data-test`, если есть. Если нет — `get_by_role("table", name="...")`.

### 2. Найти строки

```python
rows = table.locator("tbody tr")
# или, если строки лежат прямо в table:
rows = table.locator("tr")
```

Если есть `<thead>` — отдельно бери header rows и body rows, чтобы не считать
заголовок как данные:

```python
body_rows = table.locator("tbody tr")
header_cells = table.locator("thead th")
```

### 3. Конкретная строка

```python
first_row = rows.first              # первая
second_row = rows.nth(1)            # вторая (индексация с 0)
last_row = rows.last                # последняя
```

### 4. Ячейка по координатам `[row][col]`

```python
cell = rows.nth(2).locator("td").nth(1)   # 3-я строка, 2-я колонка
```

### 5. Все ячейки одной строки

```python
row_cells = rows.nth(2).locator("td")
texts = row_cells.all_inner_texts()
# ['Learn Java', 'Mukesh', 'Java', '500']
```

---

## Проверки размеров таблицы — `expect()`, не `count()`

```python
# ❌ Не auto-wait, плохая диагностика
assert rows.count() == 7

# ✅ Ждёт нужное количество, нормальная ошибка
expect(rows).to_have_count(7)
```

`to_have_count` ждёт, пока количество элементов **станет** равным ожидаемому.
Это критично, если таблица догружается через AJAX.

То же для колонок:

```python
expect(table.locator("thead th")).to_have_count(4)
```

---

## Проверка содержимого ячеек

### Точное содержимое одной ячейки

```python
expect(rows.nth(2).locator("td").nth(0)).to_have_text("Learn Java")
```

### Точное содержимое всей строки

```python
expect(rows.nth(2).locator("td")).to_have_text(
    ["Learn Java", "Mukesh", "Java", "500"]
)
```

`to_have_text(list)` — strict-проверка: и количество, и порядок, и каждое значение.

### Колонка целиком (все значения одной колонки)

```python
# Получить все ячейки 0-й колонки во всех строках
titles_loc = rows.locator("td:nth-child(1)")
titles = titles_loc.all_inner_texts()
# ['Learn Java', 'Master Selenium', 'Master Cypress']
```

`nth-child(1)` — индексация с 1 (это CSS, не Playwright).

---

## Поиск строки по содержимому — ключевой паттерн

Самая частая задача: "найди строку, где в колонке X написано Y".

```python
# ✅ Через filter + has_text
mukesh_row = rows.filter(has_text="Mukesh")

# Теперь можно работать с ней как с обычным локатором
expect(mukesh_row).to_be_visible()
expect(mukesh_row.locator("td").nth(0)).to_have_text("Learn Java")
```

Если "Mukesh" встречается в нескольких строках, `mukesh_row` будет содержать
несколько элементов — нужна более точная фильтрация:

```python
# Строки, где имя автора (3-я колонка) — ровно "Mukesh"
mukesh_rows = rows.filter(
    has=page.locator("td:nth-child(3)", has_text="Mukesh")
)
```

> ⚠️ `filter(has_text=...)` — это substring match. Если в одной строке "Mukesh",
> а в другой "Mukesh Otwani" — обе попадут в выборку. Для точного совпадения
> используй `has=page.locator("td", has_text=re.compile(r"^Mukesh$"))`.

---

## Чтение всех данных таблицы

Если нужно получить таблицу как list of dicts (для алгоритмических проверок):

```python
def read_table(rows_locator) -> list[dict]:
    headers = ["title", "author", "subject", "price"]
    result = []
    for row in rows_locator.all():
        cells = row.locator("td").all_inner_texts()
        result.append(dict(zip(headers, cells)))
    return result

# ⚠️ перед .all() — обязательно first.wait_for()
rows.first.wait_for()
data = read_table(rows)
# [{'title': 'Learn Java', 'author': 'Mukesh', 'subject': 'Java', 'price': '500'}, ...]
```

С dict-структурой удобно делать любые проверки:

```python
mukesh_books = [b for b in data if b["author"] == "Mukesh"]
assert len(mukesh_books) == 3

total = sum(int(b["price"]) for b in data)
assert total == 7100
```

---

## Агрегаты — сумма, среднее, фильтрация

Когда на странице есть строки и UI-подсчёт total — тест должен проверять, что
**total действительно равен сумме строк**. Это ловит баги в подсчётах.

```python
def test_total_equals_sum_of_rows(page):
    page.goto("/cart")
    rows = page.locator("table[data-test='cart'] tbody tr")
    rows.first.wait_for()

    # Сумма по колонке "Total" (subtotal каждого товара)
    subtotals = [
        parse_price(t)
        for t in rows.locator("td.subtotal").all_inner_texts()
    ]

    # Total с UI
    ui_total = parse_price(page.locator("[data-test='cart-total']").inner_text())

    assert sum(subtotals) == ui_total
```

Это **не дублирование UI-логики**, а проверка согласованности отображаемых
данных. Если бэкенд считает одно, а UI рисует другое — баг.

---

## Взаимодействие с контролами в строке

Часто в строке есть кнопки (удалить, редактировать, +/-). Локатор кнопки —
**относительно строки**, не по document:

```python
# ✅ Кнопка удаления в нужной строке
target_row = rows.filter(has_text="Hammer")
target_row.locator("[data-test='remove']").click()

# Дождаться, что строка пропала
expect(target_row).to_have_count(0)
```

Антипаттерн — взять кнопку из document:

```python
# ❌ Может кликнуть кнопку не в той строке
page.locator("[data-test='remove']").first.click()
```

---

## POM-паттерн: TableRow как компонент

Если со строкой делаешь больше двух операций — выноси в компонент. По аналогии
с `ProductCard` из урока 3:

```python
class CartRow:
    def __init__(self, root: Locator) -> None:
        self.root = root

    @property
    def name(self) -> Locator:
        return self.root.locator("[data-test='product-title']")

    @property
    def quantity_input(self) -> Locator:
        return self.root.locator("[data-test='product-quantity']")

    @property
    def subtotal(self) -> Locator:
        return self.root.locator("[data-test='line-price']")

    @property
    def remove_button(self) -> Locator:
        return self.root.locator("[data-test='product-remove']")

    def set_quantity(self, value: int) -> None:
        self.quantity_input.fill(str(value))

    def remove(self) -> None:
        self.remove_button.click()
```

Использование в POM страницы:

```python
class CheckoutPage(BasePage):
    PATH = "/checkout"

    @property
    def rows(self) -> Locator:
        return self.page.locator("table tbody tr")

    def row_by_name(self, name: str) -> CartRow:
        return CartRow(self.rows.filter(has_text=name))

    def all_rows(self) -> list[CartRow]:
        self.rows.first.wait_for()
        return [CartRow(self.rows.nth(i)) for i in range(self.rows.count())]
```

В тесте — никакого знания HTML:

```python
checkout = CheckoutPage(page).open()
hammer = checkout.row_by_name("Hammer")
hammer.set_quantity(3)
expect(hammer.subtotal).to_have_text("$47.97")
```

---

## Подводные камни

### 1. Stale references после удаления

Если ты сохранил локатор строки и потом удалил её — локатор станет невалидным:

```python
# ❌ Опасно
row = rows.filter(has_text="Hammer")
row.locator("[data-test='remove']").click()
# row уже относится к удалённой строке
expect(row.locator(".name")).to_have_text("Hammer")  # упадёт неочевидно
```

Лучше: после удаления **заново** получить строки.

### 2. Async-обновление после CRUD

Удалил строку → строка исчезает асинхронно (после API-ответа). Не ассерть
сразу — используй `expect`, он подождёт:

```python
row.remove()
expect(checkout.row_by_name("Hammer").root).to_have_count(0)
```

### 3. Скрытый `<thead>`

Если делаешь `table.locator("tr")` (без `tbody`) — посчитаются и header rows.
Проверь количество перед написанием теста, иначе будет `expect(rows).to_have_count(3)`,
а реально там 4 (3 данных + 1 заголовок).

```python
rows = table.locator("tbody tr")  # ✅ только данные
```

### 4. Empty state

Когда таблица пустая, сайт показывает другое (например, "No items"). Тест на
пустую таблицу нужно писать через `to_have_count(0)` и проверку текста empty
state:

```python
expect(rows).to_have_count(0)
expect(page.get_by_text("Your cart is empty")).to_be_visible()
```

### 5. Lazy loading / virtual scroll

Если таблица виртуализирована (рендерит только видимые строки), `count()`
вернёт не общее число, а **видимое**. Это редко на простых сайтах, но если
видишь, что `to_have_count` нестабилен — копай в эту сторону.

---

## Главные правила

1. **Структура таблицы → план локаторов.** Сначала открой DevTools, посмотри
   что у тебя — настоящая `<table>` или div'ы. От этого зависят селекторы.
2. **`expect(...).to_have_count(N)` — для размеров, не `count() ==`.**
3. **Поиск строки — через `filter(has_text=...)`**, а не цикл `for`.
4. **Контролы — относительно строки**, не от `page.locator(...)`.
5. **Если со строкой больше двух операций — выноси в компонент** (TableRow).
6. **Перед `.all()` — `first.wait_for()`.** Как и в уроке 7.
7. **Проверь согласованность данных** (например, total = сумма строк). Это
   ловит баги в подсчётах, которых нет в обычных UI-тестах.
