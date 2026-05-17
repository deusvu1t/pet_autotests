# Урок 7 — Методы извлечения текста и custom dropdown'ы

## О чём этот урок

Две темы:

1. **Методы извлечения текста**: `inner_text()`, `text_content()`,
   `all_inner_texts()`, `all_text_contents()`, `all()`. На первый взгляд
   они одно и то же, но различия принципиальны — особенно при работе с
   текстом, в котором есть whitespace.
2. **Custom dropdown'ы** (Bootstrap, Material UI, autosuggest). Это
   не `<select>`, и `select_option()` для них не работает. Нужен
   паттерн "click open → click option".

> Главное правило: для всех UI-проверок текста используй **`expect(...)`**.
> Извлекать текст методами ниже нужно только когда требуется получить
> **данные** для дальнейшей логики (сравнить, посчитать, передать в API).

---

## `inner_text()` vs `text_content()`

Оба возвращают строку из **одного** элемента. Различия:

| Метод            | Видит скрытое | Чистит whitespace | Возвращает при пустом    |
|------------------|---------------|-------------------|---------------------------|
| `inner_text()`   | ❌ нет        | ✅ да             | `""` (пустая строка)      |
| `text_content()` | ✅ да         | ❌ нет (`\n`, ` `)| `None`                    |

### Пример

```html
<div class="title">
   14.1-inch Laptop
</div>
```

```python
element = page.locator(".title")
element.inner_text()    # "14.1-inch Laptop"      ← чисто
element.text_content()  # "\n   14.1-inch Laptop\n"  ← сырой
```

### Когда что использовать

- **`inner_text()`** — **default**. Когда сравниваешь с видимой строкой
  ("Hello, John"), считаешь, парсишь цены.
- **`text_content()`** — когда нужен скрытый текст (например, alt-text,
  служебный текст в `display: none` элементах) или элемент гарантированно
  без whitespace.

### Подводный камень: `text_content()` возвращает `None`

```python
text = element.text_content()
text.strip()  # ❌ AttributeError: 'NoneType' object has no attribute 'strip'
```

Если используешь `text_content()` — всегда проверяй на None или используй
`inner_text()`.

```python
text = (element.text_content() or "").strip()  # безопасно
text = element.inner_text()                    # ✅ всегда строка
```

### Лучший вариант — `expect`

Если задача — **проверить** текст, используй `expect`. Он сам обрабатывает
whitespace и auto-waits:

```python
expect(element).to_have_text("14.1-inch Laptop")    # точное совпадение
expect(element).to_contain_text("Laptop")           # подстрока
```

`expect().to_have_text()` сравнивает **нормализованный** текст (как
`inner_text`), но при этом ждёт элемент и даёт хорошую диагностику.

---

## `all_inner_texts()` vs `all_text_contents()`

То же различие, но для **списка** элементов:

| Метод                  | Возвращает                            |
|------------------------|---------------------------------------|
| `all_inner_texts()`    | `list[str]` — чистые видимые тексты   |
| `all_text_contents()`  | `list[str]` — сырые тексты с whitespace |

```python
products = page.locator(".product-title")

names_clean = products.all_inner_texts()
# ['Laptop', 'Computer', 'Storage']

names_raw = products.all_text_contents()
# ['\n   Laptop   \n', '\n   Computer\n', '\n   Storage  \n']
```

### Default — `all_inner_texts()`

```python
# ❌ Тавтологичный паттерн — был во всех наших POM:
names = [n.strip() for n in product_names.all_text_contents()]

# ✅ То же одной строкой:
names = product_names.all_inner_texts()
```

`all_inner_texts()` уже чистит whitespace — `.strip()` в цикле не нужен.

### Когда `all_text_contents()` всё-таки нужен

- Когда важен скрытый текст (`display: none`)
- Когда сами whitespace значимы (редко)

---

## `all()` — Locator → `list[Locator]`

Иногда нужно итерировать по элементам и делать **разные действия** с
каждым. `all()` превращает Locator в список отдельных Locator'ов:

```python
products = page.locator(".product-title")

# ❌ all() — это РОВНО ТО, что у нас уже есть в HomePage.cards()
product_locators = products.all()
for product in product_locators:
    print(product.inner_text())
```

### Когда нужен `all()`

- Кликнуть на каждый элемент по очереди
- Выполнить **разное** действие с каждым (например, кликнуть только на
  N-й и M-й)
- Передать конкретный Locator в другой метод/компонент (как мы делаем с
  `ProductCard(card)`)

### Когда `all()` НЕ нужен

- Если просто читаешь все тексты — используй `all_inner_texts()`.
- Если делаешь одинаковое действие со всеми (например, проверка состояния) —
  используй ассерт на сам Locator: `expect(products).to_have_count(9)`.

### ⚠ Подводный камень — `all()` не ждёт

`all()` берёт **снапшот** того, что есть в DOM **прямо сейчас**. Если
элементы грузятся асинхронно — получишь пустой список.

```python
# ❌ Может вернуть [] если карточки ещё не загрузились
cards = page.locator(".product").all()

# ✅ Подождать первый, потом all()
page.locator(".product").first.wait_for()
cards = page.locator(".product").all()
```

Это же относится к `all_inner_texts()` и `all_text_contents()`.

---

## Custom dropdown'ы

Не все dropdown'ы — `<select>`. На современных сайтах часто:

- **Bootstrap dropdown** — `<button>` + `<ul role="menu">`, открывается по клику
- **Material UI / ARIA combobox** — `<div role="combobox">` + `role="listbox"`
- **Autosuggest** — input, при вводе появляется `<ul>` с вариантами

`select_option()` для них не работает. Паттерн один:

### Bootstrap / Material dropdown

```python
# 1. Открыть
menu_trigger = page.get_by_role("button", name="User menu")
menu_trigger.click()

# 2. Дождаться открытия (по появлению опции)
sign_out = page.get_by_role("menuitem", name="Sign out")
expect(sign_out).to_be_visible()

# 3. Кликнуть опцию
sign_out.click()
```

### Autosuggest

```python
search = page.get_by_role("searchbox")

# Печатаем посимвольно — autosuggest реагирует на каждый keystroke
search.press_sequentially("smart")

# Ждём появления подсказок
suggestion = page.get_by_role("option", name="smartphone")
expect(suggestion).to_be_visible()

# Кликаем
suggestion.click()
```

> Здесь `press_sequentially` имеет смысл — это **единственный** случай,
> когда он лучше `fill()`. Autosuggest реагирует на каждый keystroke, а
> `fill()` вставляет всё одним событием и подсказки могут не появиться.

### Паттерн POM для custom dropdown

```python
class UserMenu:
    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def trigger(self) -> Locator:
        return self.page.get_by_test_id("user-menu")

    @property
    def sign_out_button(self) -> Locator:
        return self.page.get_by_role("menuitem", name="Sign out")

    def open(self) -> None:
        self.trigger.click()
        expect(self.sign_out_button).to_be_visible()

    def sign_out(self) -> None:
        self.open()
        self.sign_out_button.click()
```

---

## Антипаттерны (из материалов курса)

### ❌ `expect(options).to_have_count(count)` — тавтология

```python
count = options.count()
expect(options).to_have_count(count)  # всегда True
```

Это сравнение `N == N`. Тест никогда не падает. **Это не ассерт, это шум.**

✅ Сравнивай с **ожидаемым** значением:

```python
expect(options).to_have_count(7)
# или
assert options.count() > 0
```

### ❌ `page.wait_for_timeout(3000)` после открытия dropdown'а

```python
trigger.click()
page.wait_for_timeout(3000)  # ❌
options = page.locator("...")
```

✅ Ждать появления опции:

```python
trigger.click()
expect(page.get_by_role("menuitem").first).to_be_visible()
```

### ❌ `print()` для проверок

```python
print("5th option:", options.nth(5).inner_text())
```

Это лог, а не тест. В нормальном тесте — ассерт.

### ❌ `page.locator("form i").nth(2)`

```python
page.locator("form i").nth(2).click()  # 3-я иконка — какая?
```

Локатор не говорит, что кликаем. Используй роль, имя, test-id.

### ❌ Цикл с break вместо прямого клика

```python
# Из материалов курса
for i in range(count):
    text = options.nth(i).inner_text()
    if text == 'Finance Manager':
        options.nth(i).click()
        break
```

✅ Прямой клик по тексту:

```python
page.get_by_role("option", name="Finance Manager").click()
```

---

## Главные тейкауэи

1. **`inner_text()` / `all_inner_texts()`** — default. Чистый
   видимый текст.
2. **`text_content()`** — только когда нужен скрытый текст или
   точные whitespace. Помнить про `None`.
3. **`expect(...)`** — для проверок текста. Не дёргай `inner_text()` ради
   `assert`.
4. **`all()`** — для итерации с разными действиями. Не для просто чтения
   текста. **Ждёт явно**, через `first.wait_for()`.
5. **Custom dropdown** — `click открыть → click опцию`. Между ними —
   `expect(option).to_be_visible()`, не `wait_for_timeout`.
6. **Autosuggest** — `press_sequentially` (единственный честный случай).
7. **`expect(loc).to_have_count(loc.count())` — это не тест, это шум.**
