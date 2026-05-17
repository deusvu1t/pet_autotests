# Урок 6 — Dropdown'ы

## О чём этот урок

После урока 5 ты умеешь работать с `<select>` через `select_option()`. Но это
половина истории. На реальных сайтах есть два типа dropdown'ов:

1. **Native `<select>`** — стандартный HTML-элемент. С ним работает
   `select_option()`.
2. **Custom dropdown** (ARIA combobox) — стилизованный `<div>` с
   `role="listbox"`. С ним `select_option()` не работает — нужен паттерн
   "клик-открыть, клик-выбрать".

Кроме того, dropdown — это **источник данных**. Часто тесты проверяют не
"я выбрал X", а "какие опции вообще есть" и "в каком порядке".

---

## Native `<select>` — повторение и углубление

### Три способа выбрать опцию

```python
dropdown = page.get_by_label("Country")

dropdown.select_option(label="United States")   # по видимому тексту
dropdown.select_option(value="US")              # по HTML-атрибуту value
dropdown.select_option(index=2)                 # по позиции (с 0)
```

**Когда какой использовать:**
- `label=` — **default**. Читаемо, тест говорит сам за себя.
- `value=` — если `value` стабильнее `label` (например, `value="us-east-1"`,
  а label локализуется в зависимости от языка).
- `index=` — **только** когда других вариантов нет (порядок гарантирован
  бизнес-логикой, например "первая опция в списке").

### Multi-select

Тот же метод, но передаём **список**:

```python
colors = page.get_by_label("Colors")

colors.select_option(["Red", "Blue", "Green"])           # по labels
colors.select_option(label=["Red", "Blue"])              # явно по labels
colors.select_option(value=["red", "blue"])              # по values
colors.select_option(index=[0, 2, 4])                    # по индексам
```

Multi-select работает **только** на `<select multiple>`. Если атрибута
`multiple` нет — Playwright выберет только последнюю опцию из списка.

### Снять выделение в multi-select

```python
colors.select_option([])   # пустой список = снять всё
```

---

## Чтение содержимого dropdown'а

Часто dropdown — это **тест на данные**. Например: "в выпадашке стран должна
быть Канада". Это типовая регрессионная проверка.

### Получить все опции как список

```python
dropdown = page.get_by_label("Country")
options = dropdown.locator("option").all_text_contents()
# ['Choose...', 'United States', 'Canada', 'Germany', ...]
```

`all_text_contents()` возвращает `list[str]`. **Не путать** с `text_content()`
(одна строка для одного элемента).

### Проверки количества и наличия

```python
options_locator = dropdown.locator("option")

# Точное количество
expect(options_locator).to_have_count(10)

# Конкретная опция присутствует
expect(options_locator).to_contain_text(["United States"])

# Все опции — массив значений (порядок важен)
expect(options_locator).to_have_text(["Choose...", "Hand Tools", "Power Tools"])
```

> `to_have_text(list)` — strict-проверка: количество и значения должны
> совпасть один-в-один. `to_contain_text(list)` — каждый элемент массива
> должен встретиться хотя бы где-то в локаторе.

### Текущее выбранное значение

```python
selected = dropdown.input_value()  # str — текущее value
# или ассерт:
expect(dropdown).to_have_value("name,asc")
```

`input_value()` возвращает **value** опции, не **label**. Чтобы получить
видимый текст — нужен дополнительный поиск:

```python
selected_label = dropdown.locator("option:checked").text_content()
```

---

## Проверка сортировки

Базовый паттерн: сравнить полученный список с тем, что получится при
сортировке Python:

```python
options = dropdown.locator("option").all_text_contents()
options = [o.strip() for o in options]  # чистим whitespace

assert options == sorted(options), f"Dropdown not sorted: {options}"
```

Или, если первая опция — placeholder ("Choose..."):

```python
options = dropdown.locator("option").all_text_contents()[1:]  # skip placeholder
assert options == sorted(options)
```

### Сортировка с парсингом — цены, числа

Если в dropdown'е тексты типа `"$14.99"`, обычный `sorted` отсортирует их как
строки (`"$10" < "$2"`). Нужно парсить:

```python
from utils.parsers import parse_price

prices_text = page.locator("[data-test='product-price']").all_text_contents()
prices = [parse_price(p) for p in prices_text]

assert prices == sorted(prices), "Products not sorted by price ascending"
```

`parse_price` из урока 4 — `float(text.replace("$", "").strip())`.

### Reverse-сортировка

```python
assert prices == sorted(prices, reverse=True)
```

---

## Custom dropdown'ы (не `<select>`)

На современных сайтах часто dropdown — это `<div>` с `role="combobox"` или
`role="listbox"`. Признак: посмотри в DevTools, если корневой элемент **не**
`<select>` — это custom dropdown.

`select_option()` на нём **не работает**. Паттерн:

```python
# 1. Кликнуть на элемент, чтобы открыть список
page.get_by_role("combobox", name="Country").click()

# 2. Кликнуть на нужную опцию (по тексту или role="option")
page.get_by_role("option", name="United States").click()

# 3. Проверить выбранное значение
expect(page.get_by_role("combobox", name="Country")).to_contain_text("United States")
```

### Чтение опций custom dropdown'а

Часто опции отображаются только когда dropdown открыт. Сначала открыть,
потом читать:

```python
combobox = page.get_by_role("combobox", name="Country")
combobox.click()

options = page.get_by_role("option").all_text_contents()
expect(page.get_by_role("option")).to_have_count(50)

combobox.click()  # закрыть обратно (или Esc)
```

> На practicesoftwaretesting.com все dropdown'ы — native `<select>`. Custom
> dropdown'ы встречаются на сайтах с React/Material UI/Ant Design. Знать
> паттерн нужно — на собеседованиях спрашивают.

---

## Паттерны POM для dropdown'ов

### Метод "выбрать опцию"

```python
class HomePage(BasePage):
    @property
    def sort_dropdown(self) -> Locator:
        return self.page.get_by_test_id("sort")

    def sort_by(self, option: str) -> None:
        self.sort_dropdown.select_option(label=option)
```

### Метод "получить список опций"

```python
def sort_options(self) -> list[str]:
    return [o.strip() for o in self.sort_dropdown.locator("option").all_text_contents()]
```

### Метод "выбрать и дождаться обновления"

Это самый важный паттерн — после `select_option` нужно убедиться, что
страница реально перерисовалась. Простой `select_option` сам по себе **не
ждёт** перерисовку результата.

```python
def sort_by(self, option: str) -> None:
    first_card = self.product_cards.first
    old_text = first_card.text_content()
    self.sort_dropdown.select_option(label=option)
    expect(first_card).not_to_have_text(old_text)  # ждём изменения
```

Альтернатива — ждать сетевой запрос:

```python
with self.page.expect_response("**/products?sort=*"):
    self.sort_dropdown.select_option(label=option)
```

---

## Антипаттерны

### ❌ `print()` вместо ассертов

```python
# Из материалов курса:
if original_list == sorted_list:
    print("dropdown options are sorted order...")
else:
    print("dropdown options are Not sorted order.")
```

`print` ничего не проверяет — тест всегда зелёный. **Это не тест, это
лог.** Правильно:

```python
assert options == sorted(options)
```

### ❌ `page.wait_for_timeout(5000)` после `select_option`

```python
# ❌
dropdown.select_option(label="Lowest to highest")
page.wait_for_timeout(3000)

# ✅
dropdown.select_option(label="Lowest to highest")
expect(first_card).not_to_have_text(old_text)
```

### ❌ Чтение через `text_content()` и сравнение строк цен

```python
# ❌ "$10" > "$2" как строка
prices = page.locator(".price").all_text_contents()
assert prices == sorted(prices)
```

Нужен парсинг в `float`.

### ❌ `to_have_count(10)` без понимания

Курс пишет `to_have_count(10)`, ничего не сверяя со смыслом. Если завтра в
dropdown появится новая страна — тест упадёт **не по делу**. Если конкретное
число важно для бизнеса — пиши его с комментарием. Иначе проверяй
**содержимое**, а не количество.

### ❌ `select_option(index=N)` "потому что так короче"

Индекс ломается при любом изменении порядка. Используй `label=` или `value=`.

---

## Главные тейкауэи

1. **`<select>` — `select_option()`. Custom — клик-клик.**
2. **Label > value > index** для выбора. Index — последняя мера.
3. **Multi-select — список в `select_option`.** Пустой список = снять всё.
4. **Чтение опций — `locator("option").all_text_contents()`** + `to_have_count`
   / `to_contain_text` / `to_have_text(list)`.
5. **Проверка сортировки — `assert list == sorted(list)`** с парсингом
   для чисел.
6. **После `select_option`** — ждать перерисовки через `expect()` на
   изменение, не `wait_for_timeout`.
7. **`print()` — не ассерт.** В тесте либо `assert`, либо `expect()`.
