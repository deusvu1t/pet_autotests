# Шпаргалка — урок 6 (dropdown'ы)

## Native `<select>` — выбор опции

```python
dropdown = page.get_by_label("Country")

dropdown.select_option(label="United States")  # ✅ default
dropdown.select_option(value="US")             # стабильное value
dropdown.select_option(index=2)                # последнее средство
```

| Способ    | Когда использовать                                  |
|-----------|------------------------------------------------------|
| `label=`  | Default — читаемо, говорит само за себя.            |
| `value=`  | Когда `value` стабильнее label (локализация и т.п.). |
| `index=`  | Только когда других вариантов нет.                  |

---

## Multi-select

```python
colors = page.get_by_label("Colors")

colors.select_option(["Red", "Blue"])                # by labels (default)
colors.select_option(label=["Red", "Blue"])          # явно
colors.select_option(value=["red", "blue"])          # by values
colors.select_option(index=[0, 2])                   # by indexes
colors.select_option([])                             # снять всё
```

> Работает только на `<select multiple>`. Без `multiple` — выбирается
> последний.

---

## Чтение опций

```python
options_loc = dropdown.locator("option")

# Все тексты
options = [o.strip() for o in options_loc.all_text_contents()]

# Ассерты
expect(options_loc).to_have_count(10)
expect(options_loc).to_contain_text(["United States", "Canada"])
expect(options_loc).to_have_text(["A", "B", "C"])     # strict — точное совпадение
```

| Ассерт                  | Что проверяет                                |
|-------------------------|----------------------------------------------|
| `to_have_count(N)`      | Количество опций.                            |
| `to_contain_text(list)` | Каждый элемент списка встречается где-то.    |
| `to_have_text(list)`    | **Strict** — порядок и количество совпадают. |

---

## Текущее значение

```python
dropdown.input_value()                              # возвращает str (value)
expect(dropdown).to_have_value("price,asc")         # ассерт на value

# Видимый label выбранной опции
dropdown.locator("option:checked").text_content()
```

`input_value()` отдаёт **value**, не label. Это важно.

---

## Проверка сортировки

```python
options = [o.strip() for o in dropdown.locator("option").all_text_contents()]

# Алфавитная сортировка
assert options == sorted(options)

# Обратная
assert options == sorted(options, reverse=True)

# С парсингом (для цен и чисел)
from utils.parsers import parse_price
prices = [parse_price(p) for p in price_locator.all_text_contents()]
assert prices == sorted(prices)
```

> `sorted("$10", "$2")` → `["$10", "$2"]` (строковая сортировка). Парсь в
> `float`.

---

## Custom dropdown (combobox)

```python
# 1. Открыть
page.get_by_role("combobox", name="Country").click()

# 2. Выбрать опцию
page.get_by_role("option", name="United States").click()

# 3. Проверить
expect(page.get_by_role("combobox", name="Country")).to_contain_text(
    "United States"
)
```

`select_option()` для custom dropdown **не работает**.

---

## Ожидание после select_option

`select_option` сам по себе **не ждёт** перерисовку сетки. После него либо:

```python
# Через ожидание изменения
old_text = first_card.text_content()
dropdown.select_option(label="Price (Low - High)")
expect(first_card).not_to_have_text(old_text)
```

```python
# Через ожидание запроса
with page.expect_response("**/products?sort=*"):
    dropdown.select_option(label="Price (Low - High)")
```

---

## POM-методы

```python
class HomePage(BasePage):
    @property
    def sort_dropdown(self) -> Locator:
        return self.page.get_by_test_id("sort")

    def sort_by(self, option: str) -> None:
        old = self.product_cards.first.text_content()
        self.sort_dropdown.select_option(label=option)
        expect(self.product_cards.first).not_to_have_text(old or "")

    def sort_options(self) -> list[str]:
        return [
            o.strip()
            for o in self.sort_dropdown.locator("option").all_text_contents()
        ]
```

---

## Антипаттерны

| ❌                                       | ✅                                                |
|-----------------------------------------|--------------------------------------------------|
| `print("sorted!")` для проверки         | `assert options == sorted(options)`              |
| `page.wait_for_timeout(3000)`           | `expect(card).not_to_have_text(old)`             |
| `sorted(["$10", "$2"])` как строки      | `sorted([parse_price(p) for p in prices])`       |
| `to_have_count(10)` без смысла          | `to_contain_text(["конкретные опции"])`          |
| `select_option(index=3)` без причины    | `select_option(label="United States")`           |
| `select_option` на custom dropdown      | `combobox.click()` + `option.click()`            |

---

## Быстрая памятка

1. **`<select>` → `select_option`. Custom → клик-клик.**
2. **`label=` >> `value=` >> `index=`.**
3. **Multi-select** — список в аргумент. Пустой — снять всё.
4. **Чтение** — `locator("option").all_text_contents()`, `to_have_text(list)`.
5. **Сортировка** — `assert list == sorted(list)`. Для цен — парсинг.
6. **Ждать после select_option** — через `expect()` на UI, не таймаут.
7. **`print()` — не тест.**
