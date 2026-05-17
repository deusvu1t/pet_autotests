# Шпаргалка — урок 5 (формы и элементы ввода)

## Локаторы для форм (приоритет)

```
get_by_label  →  get_by_placeholder  →  get_by_role("textbox", name=)
              →  get_by_test_id  →  CSS  →  XPath
```

`get_by_label` — основной выбор для форм. Использует HTML связку `<label>` ↔ `<input>`.

---

## Текстовые инпуты

| Метод                       | Что делает                                    |
|-----------------------------|------------------------------------------------|
| `fill(value)`               | Очищает + вставляет одним событием. **99% случаев.** |
| `clear()`                   | Очищает (то же что `fill("")`).                |
| `press_sequentially(text)`  | Посимвольный ввод. Только для autocomplete.    |
| `press(key)`                | Одна клавиша: `"Enter"`, `"Tab"`, `"Control+A"`. |
| `input_value()`             | Текущее значение. Возвращает `str` — для логики. |
| `type(text)`                | **Deprecated.** Не использовать.               |

```python
page.get_by_label("Email").fill("user@test.com")
page.get_by_label("Email").press("Tab")
value = page.get_by_label("Email").input_value()
```

---

## Чекбоксы

| Метод                  | Что делает                                |
|------------------------|--------------------------------------------|
| `check()`              | Поставить (идемпотентно).                  |
| `uncheck()`            | Снять (идемпотентно).                      |
| `set_checked(True)`    | Явно True.                                  |
| `set_checked(False)`   | Явно False.                                 |
| `is_checked()`         | `bool` — для условной логики.              |

```python
checkbox = page.get_by_label("Subscribe")
checkbox.check()
expect(checkbox).to_be_checked()
```

### Batch — итерация по labels

```python
for day in ["Mon", "Tue", "Wed"]:
    page.get_by_label(day).check()
```

---

## Radio buttons

```python
page.get_by_label("Male").check()
expect(page.get_by_label("Male")).to_be_checked()
expect(page.get_by_label("Female")).not_to_be_checked()
```

> ⚠ `uncheck()` для radio **не работает**. Чтобы "снять" — выбери другой в группе.

---

## Select (`<select>`)

```python
dropdown = page.get_by_label("Country")

dropdown.select_option(label="United States")  # ✅ читаемое
dropdown.select_option(value="US")             # стабильное
dropdown.select_option(index=2)                # последнее средство

# multi-select
dropdown.select_option(["Red", "Blue"])
```

---

## Textarea

То же API, что text input:

```python
textarea.fill("Line 1\nLine 2")
expect(textarea).to_have_value("Line 1\nLine 2")
```

---

## Файлы — `set_input_files`

```python
file_input = page.locator("input[type='file']")

file_input.set_input_files("path/to/file.pdf")
file_input.set_input_files(["a.png", "b.png"])     # несколько
file_input.set_input_files([])                     # очистить

# Без файла на диске:
file_input.set_input_files({
    "name": "test.txt",
    "mimeType": "text/plain",
    "buffer": b"content",
})
```

---

## Состояния — ассерты

| Ассерт                          | Что проверяет                                  |
|---------------------------------|-------------------------------------------------|
| `to_be_visible`                 | Видим                                           |
| `to_be_hidden`                  | Скрыт                                           |
| `to_be_enabled` / `to_be_disabled` | Активен / заблокирован                       |
| `to_be_editable`                | Можно редактировать (не readonly)               |
| `to_be_focused`                 | В фокусе                                        |
| `to_be_empty`                   | Пустой (`value == ""`)                          |
| `to_be_checked` / `not_to_be_checked` | Чекбокс/radio состояние                   |
| `to_have_value`                 | Значение                                        |
| `to_have_text`                  | Текст                                           |
| `to_have_attribute`             | Атрибут                                         |
| `to_have_count`                 | Количество элементов                            |

---

## Атрибуты

```python
# expect — для проверок
expect(input).to_have_attribute("type", "email")
expect(input).to_have_attribute("required", "")
expect(input).to_have_attribute("aria-invalid", "true")

# get_attribute — для данных
maxlen = input.get_attribute("maxlength")
```

---

## Валидация форм

| Что проверять                  | Как                                         |
|--------------------------------|----------------------------------------------|
| Тип поля                       | `to_have_attribute("type", "email")`         |
| Обязательность                 | `to_have_attribute("required", "")`          |
| После ошибки                   | `to_have_attribute("aria-invalid", "true")`  |
| Текст ошибки                   | `expect(page.get_by_text("...")).to_be_visible()` |
| Native validity (продвинутое)  | `input.evaluate("el => el.validationMessage")` |

---

## Паттерны POM

```python
class RegisterPage(BasePage):
    PATH = "/auth/register"

    def register(self, data: dict) -> None:
        self.page.get_by_label("First name").fill(data["first_name"])
        self.page.get_by_label("Email address").fill(data["email"])
        self.page.get_by_label("Password").fill(data["password"])
        self.page.get_by_label("Country").select_option(label=data["country"])
        self.page.get_by_role("button", name="Register").click()
```

---

## Антипаттерны

| ❌                                              | ✅                                              |
|------------------------------------------------|------------------------------------------------|
| `press_sequentially("text")` без autocomplete  | `fill("text")`                                 |
| `.type("text")` (deprecated)                   | `fill("text")` или `press_sequentially()`      |
| `assert input.input_value() == "X"`            | `expect(input).to_have_value("X")`             |
| `assert checkbox.is_checked()`                 | `expect(checkbox).to_be_checked()`             |
| `page.wait_for_timeout(2000)` после fill       | ничего — auto-wait работает                    |
| `page.locator("input").nth(2).fill(...)`       | `page.get_by_label("First name").fill(...)`    |
| Хардкод данных в тесте                         | `utils/test_data.py` или Faker                 |
| `radio.uncheck()`                              | Выбрать другой radio в той же группе           |

---

## Быстрая памятка

1. **`get_by_label`** для форм — практически всегда.
2. **`fill()` для текста** — `press_sequentially` только если есть autocomplete.
3. **`expect(...)` для UI**, `input_value()` / `get_attribute()` — для данных.
4. **Checkbox vs radio:** оба `check()`, но `uncheck` для radio бесполезен.
5. **Select:** `label=` — самое читаемое.
6. **Файлы:** `set_input_files`, никаких кликов по диалогу.
7. **Данные в `utils/test_data.py` или через Faker** — не в тестах.
