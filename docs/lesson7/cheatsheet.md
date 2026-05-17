# Шпаргалка — урок 7 (извлечение текста + custom dropdown)

## Один элемент — текст

| Метод            | Видит скрытое | Чистит whitespace | Пустой элемент       |
|------------------|---------------|-------------------|----------------------|
| `inner_text()`   | ❌            | ✅                | `""`                 |
| `text_content()` | ✅            | ❌                | **`None`**           |

```python
element.inner_text()      # "Hello"               ← default
element.text_content()    # "\n   Hello   \n"     ← редко
```

> `text_content()` может вернуть **`None`** — `.strip()` сразу падает.

```python
text = (element.text_content() or "").strip()    # безопасно
```

---

## Много элементов — текст

| Метод                  | Возвращает                          |
|------------------------|-------------------------------------|
| `all_inner_texts()`    | `list[str]` — чистые тексты         |
| `all_text_contents()`  | `list[str]` — сырые с whitespace    |

```python
# ❌ Старый паттерн
names = [n.strip() for n in products.all_text_contents()]

# ✅ Одной строкой
names = products.all_inner_texts()
```

---

## `all()` — Locator → `list[Locator]`

```python
products_loc = page.locator(".product")
products_loc.first.wait_for()            # обязательно — all() не ждёт!
products = products_loc.all()

for product in products:
    product.locator(".name").click()
```

**Когда нужен:**
- Кликать на каждый по очереди
- Разные действия с разными элементами
- Передать конкретный Locator в компонент: `ProductCard(card)`

**Когда не нужен:**
- Чтение текстов → `all_inner_texts()`
- Проверка количества → `expect(loc).to_have_count(N)`

---

## Проверки текста — `expect()`, не `inner_text()`

```python
# ❌ Нет auto-wait, плохая диагностика
assert element.inner_text() == "Hello"

# ✅ Auto-waits, чёткое сообщение об ошибке
expect(element).to_have_text("Hello")
expect(element).to_contain_text("Hell")
```

| Ассерт                | Что проверяет                                  |
|-----------------------|-------------------------------------------------|
| `to_have_text`        | Точное совпадение (нормализован whitespace)     |
| `to_contain_text`     | Подстрока                                       |
| `to_have_text(list)`  | Strict — массив текстов на массиве элементов    |
| `to_contain_text(list)` | Каждый элемент массива встречается             |

---

## Custom dropdown (Bootstrap / Material)

```python
# 1. Открыть
trigger = page.get_by_role("button", name="User menu")
trigger.click()

# 2. Дождаться появления опции (НЕ wait_for_timeout!)
sign_out = page.get_by_role("menuitem", name="Sign out")
expect(sign_out).to_be_visible()

# 3. Кликнуть
sign_out.click()
```

### POM-паттерн

```python
class UserMenu:
    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def trigger(self) -> Locator:
        return self.page.get_by_test_id("nav-menu")

    @property
    def sign_out(self) -> Locator:
        return self.page.get_by_test_id("nav-sign-out")

    def open(self) -> None:
        self.trigger.click()
        expect(self.sign_out).to_be_visible()
```

---

## Autosuggest

```python
search = page.get_by_role("searchbox")

# ⚠ press_sequentially, не fill! Autosuggest реагирует на каждый keystroke
search.press_sequentially("smart")

# Дождаться появления подсказки
suggestion = page.get_by_role("option", name="smartphone")
expect(suggestion).to_be_visible()
suggestion.click()
```

> Это **единственный** случай, где `press_sequentially` лучше `fill()`.

---

## Антипаттерны

| ❌                                                  | ✅                                              |
|----------------------------------------------------|-------------------------------------------------|
| `[s.strip() for s in loc.all_text_contents()]`     | `loc.all_inner_texts()`                         |
| `loc.text_content().strip()`                       | `loc.inner_text()` или `(text or "").strip()`   |
| `expect(loc).to_have_count(loc.count())`           | `expect(loc).to_have_count(9)` (ожидаемое)      |
| `assert el.inner_text() == "X"`                    | `expect(el).to_have_text("X")`                  |
| `trigger.click(); page.wait_for_timeout(3000)`     | `trigger.click(); expect(item).to_be_visible()` |
| `print("count:", loc.count())` как "проверка"      | `assert loc.count() == 9`                       |
| `for ... if text == "X": .click(); break`          | `page.get_by_role("option", name="X").click()`  |
| `loc.all()` без `.first.wait_for()` перед ним      | `loc.first.wait_for(); cards = loc.all()`       |

---

## Быстрая памятка

1. **`inner_text()` / `all_inner_texts()`** — default.
2. **`text_content()`** — редко. Помни про `None`.
3. **Проверки текста** — `expect()`, не `inner_text()` + `assert`.
4. **`all()`** — для разных действий, не для чтения текстов. Перед ним —
   `first.wait_for()`.
5. **Custom dropdown** — `click open → expect(option).to_be_visible() →
   click option`.
6. **Autosuggest** — `press_sequentially`, не `fill`.
7. **`expect(...).to_have_count(loc.count())` — мусор**. Сравнивай с
   ожидаемым числом.
