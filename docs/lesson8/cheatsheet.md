# Шпаргалка — урок 8 (статические таблицы)

## HTML-таблица — структура

```html
<table>
  <thead>
    <tr><th>Title</th><th>Author</th></tr>
  </thead>
  <tbody>
    <tr><td>Java</td><td>Mukesh</td></tr>
  </tbody>
</table>
```

| Тег       | Что                                     |
|-----------|-----------------------------------------|
| `<table>` | Контейнер                               |
| `<tr>`    | Row — строка                            |
| `<th>`    | Header cell — обычно внутри `<thead>`   |
| `<td>`    | Data cell                               |

> ⚠️ На SPA таблица может быть из `<div>` с `role="row"` / CSS Grid.
> Сначала смотришь DevTools — потом пишешь локаторы.

---

## Базовые локаторы

```python
table = page.locator("table[data-test='cart']")
rows = table.locator("tbody tr")               # только данные, без header
headers = table.locator("thead th")

first_row = rows.first
nth_row = rows.nth(2)                          # 3-я строка (с 0)
last_row = rows.last

cell = rows.nth(2).locator("td").nth(1)        # [row=2][col=1]
all_cells_in_row = rows.nth(2).locator("td")
```

---

## Проверки размеров

```python
expect(rows).to_have_count(7)                  # ✅ auto-wait
expect(headers).to_have_count(4)

# ❌ assert rows.count() == 7  — нет auto-wait
```

---

## Чтение содержимого

```python
# Одна ячейка
cell.inner_text()

# Вся строка как список
rows.nth(2).locator("td").all_inner_texts()
# ['Learn Java', 'Mukesh', 'Java', '500']

# Колонка целиком
rows.locator("td:nth-child(1)").all_inner_texts()
# ['Learn Java', 'Master Selenium', ...]
```

---

## Проверка содержимого

```python
# Одна ячейка
expect(cell).to_have_text("Learn Java")

# Вся строка strict
expect(rows.nth(2).locator("td")).to_have_text(
    ["Learn Java", "Mukesh", "Java", "500"]
)
```

---

## Поиск строки по содержимому — KEY PATTERN

```python
# Подстрока
row = rows.filter(has_text="Mukesh")

# Точное совпадение в конкретной колонке
import re
row = rows.filter(
    has=page.locator("td:nth-child(2)", has_text=re.compile(r"^Mukesh$"))
)
```

> Никаких `for row in rows.all(): if row.locator(...).inner_text() == "X"` —
> это антипаттерн. `filter()` делает это декларативно.

---

## Чтение всей таблицы в list[dict]

```python
rows.first.wait_for()                          # обязательно перед .all()

headers_names = ["title", "author", "subject", "price"]
data = [
    dict(zip(headers_names, row.locator("td").all_inner_texts()))
    for row in rows.all()[1:]                  # [1:] — skip <th> row
]

mukesh = [b for b in data if b["author"] == "Mukesh"]
total = sum(int(b["price"]) for b in data)
```

---

## Действия в строке

```python
# ✅ Кнопка относительно своей строки
row = rows.filter(has_text="Hammer")
row.locator("[data-test='remove']").click()
expect(row).to_have_count(0)

# ❌ От document — может попасть в другую строку
page.locator("[data-test='remove']").first.click()
```

---

## TableRow как компонент (POM)

```python
class CartRow:
    def __init__(self, root: Locator) -> None:
        self.root = root

    @property
    def name(self) -> Locator:
        return self.root.locator("[data-test='product-title']")

    @property
    def subtotal(self) -> Locator:
        return self.root.locator("[data-test='line-price']")

    def set_quantity(self, value: int) -> None:
        self.root.locator("[data-test='product-quantity']").fill(str(value))

    def remove(self) -> None:
        self.root.locator("[data-test='product-remove']").click()
```

Использование:

```python
hammer = checkout.row_by_name("Hammer")
hammer.set_quantity(3)
expect(hammer.subtotal).to_have_text("$47.97")
```

---

## Кросс-проверка: total = сумма строк

```python
subtotals = [
    parse_price(t)
    for t in rows.locator("[data-test='line-price']").all_inner_texts()
]
ui_total = parse_price(page.locator("[data-test='cart-total']").inner_text())

assert round(sum(subtotals), 2) == round(ui_total, 2)
```

Ловит арифметические баги, которых обычные UI-тесты не видят.

---

## Антипаттерны

| ❌                                              | ✅                                        |
|-------------------------------------------------|-------------------------------------------|
| `assert rows.count() == 7`                      | `expect(rows).to_have_count(7)`           |
| `for row in rows.all(): if ... break`           | `rows.filter(has_text=...)`               |
| `table.locator("tr")` (считает thead)           | `table.locator("tbody tr")`               |
| `page.locator("[data-test='remove']").click()`  | `row.locator("[data-test='remove']")...`  |
| `rows.all()` без `first.wait_for()`             | `rows.first.wait_for(); rows.all()`       |
| Чтение row после `remove()`                     | Получи строки заново                      |
| Хардкод индекса колонки везде                   | Вынеси в TableRow-компонент               |

---

## Быстрая памятка

1. **Открой DevTools** — `<table>` или div'ы? От этого зависит всё.
2. **`tbody tr`** — иначе посчитаешь header.
3. **`expect(rows).to_have_count(N)`**, не `rows.count() ==`.
4. **`filter(has_text=...)`** — поиск строки. Не цикл.
5. **Кнопки — относительно `row`**, не от `page`.
6. **Перед `.all()`** — `first.wait_for()`.
7. **Больше двух операций со строкой** — выноси в `TableRow`.
8. **Проверь total против суммы строк** — это уникальная сила таблиц.
