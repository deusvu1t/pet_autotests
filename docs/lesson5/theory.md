# Урок 5 — Формы и элементы ввода

## О чём этот урок

После уроков 1-4 ты умеешь находить элементы. Теперь — **взаимодействовать** с
ними. На любом сайте формы это:
- Текстовые инпуты (имя, email, пароль)
- Чекбоксы (фильтры, согласие с условиями)
- Радио-кнопки (выбор одного варианта)
- Селекты (`<select>`, dropdown)
- Textarea (комментарии, сообщения)
- Файловые инпуты (загрузка)

Playwright даёт **высокоуровневое** API для каждого типа. Главное — выбрать
правильный метод и правильный ассерт.

---

## Локаторы для форм — `get_by_label` это король

Для форм у Playwright есть идеальный локатор — `get_by_label`. Он работает с
`<label>` ↔ `<input>` связкой через `for`/`id` или вложенность:

```html
<label for="email">Email address</label>
<input id="email" type="email">

<!-- или вложенность -->
<label>Email address <input type="email"></label>
```

```python
page.get_by_label("Email address").fill("test@test.com")
```

**Почему `get_by_label`** лучше `get_by_test_id` для форм:
- Тест читается как пользовательский сценарий
- Работает на сайтах без `data-test`
- Падает с понятным сообщением, если label-input связка сломалась
  (это реальный баг доступности)

Если label нет — `get_by_placeholder`, `get_by_role("textbox", name=...)`,
и только потом `get_by_test_id` / CSS.

---

## Текстовые инпуты

### `fill()` — основной метод

```python
page.get_by_label("Email").fill("user@example.com")
```

Что делает `fill()`:
1. Ждёт элемент до 5 секунд (auto-wait)
2. Очищает значение
3. Вставляет текст одним событием

**Это правильный выбор в 99% случаев.**

### `clear()` — очистить

```python
page.get_by_label("Search").clear()
```

То же, что `fill("")`, но семантически чище.

### `press_sequentially()` — посимвольный ввод

Раньше назывался `type()`. Имитирует реального пользователя — каждый символ
триггерит keydown/keyup/input события.

```python
page.get_by_label("Search").press_sequentially("hammer", delay=100)
```

**Когда нужен:**
- На странице есть **autocomplete**, который реагирует на каждый символ
- Нужно симулировать пользовательский ввод для тестирования UX
- Есть валидация "на ходу" по каждому keystroke

**В 99% случаев — `fill()`.** `press_sequentially` медленнее и хрупче.

> ⚠ Метод `type()` устарел (deprecated) с Playwright 1.40+. Используй
> `press_sequentially()`.

### `press()` — конкретная клавиша

```python
page.get_by_label("Search").press("Enter")
page.get_by_label("Email").press("Tab")
page.get_by_label("Name").press("Control+A")  # выделить всё
```

### Чтение значения

```python
# input_value() возвращает текущее значение поля
value = page.get_by_label("Email").input_value()
# Используй для assert на чистые данные

# expect — для UI-проверок
expect(page.get_by_label("Email")).to_have_value("user@example.com")
```

**Правило:** UI-проверка → `expect(...).to_have_value(...)`. Данные для
дальнейшей логики → `input_value()`.

---

## Атрибуты — `get_attribute` vs `to_have_attribute`

```python
# expect — для UI-проверок (auto-wait, понятная диагностика)
expect(password).to_have_attribute("type", "password")
expect(input).to_have_attribute("maxlength", "15")

# get_attribute — для получения значения в коде
maxlength = name_input.get_attribute("maxlength")
if int(maxlength) < 100:
    ...
```

**Правило то же:** проверка → `expect`. Использование значения → `get_attribute`.

### Полезные ассерты атрибутов

```python
expect(input).to_have_attribute("type", "email")
expect(input).to_have_attribute("required", "")  # required просто есть
expect(input).to_have_attribute("aria-invalid", "true")  # после ошибки валидации
```

---

## Чекбоксы

### Базовые действия

```python
checkbox = page.get_by_label("Subscribe to newsletter")

checkbox.check()      # поставить (если не стоит)
checkbox.uncheck()    # снять (если стоит)
checkbox.set_checked(True)   # явно True
checkbox.set_checked(False)  # явно False

is_on = checkbox.is_checked()  # bool
```

`check()` и `uncheck()` идемпотентны — если уже в нужном состоянии,
просто проходят.

### Ассерты

```python
expect(checkbox).to_be_checked()
expect(checkbox).not_to_be_checked()
```

### Batch-операции — итерация

```python
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# Поставить все
for day in days:
    page.get_by_label(day).check()

# Снять все
for day in days:
    page.get_by_label(day).uncheck()

# Toggle
for day in days:
    checkbox = page.get_by_label(day)
    if checkbox.is_checked():
        checkbox.uncheck()
    else:
        checkbox.check()
```

### Антипаттерн: индексы

```python
# Плохо — хрупко, если порядок изменится
checkboxes = page.locator("input[type='checkbox']")
checkboxes.nth(2).check()

# Хорошо — по смысловой метке
page.get_by_label("Wednesday").check()
```

---

## Radio buttons

Технически — те же чекбоксы. Разница: **взаимоисключающие** (один в группе).

```python
gender_male = page.get_by_label("Male")
gender_female = page.get_by_label("Female")

gender_male.check()
expect(gender_male).to_be_checked()
expect(gender_female).not_to_be_checked()

# После выбора Female — Male автоматически снимется (это поведение браузера)
gender_female.check()
expect(gender_male).not_to_be_checked()
```

> ⚠ Для radio **нельзя** использовать `uncheck()` — оно ничего не делает.
> Чтобы "снять" radio, нужно выбрать другой в той же группе.

### Выбор по условию

```python
colors = ["Red", "Blue", "Green", "Yellow"]
chosen = "Green"

# Хорошо
page.get_by_label(chosen).check()

# Лишнее (антипаттерн — цикл там, где он не нужен)
for color in colors:
    if color == chosen:
        page.get_by_label(color).check()
```

---

## Селекты (`<select>`) — повтор после урока 4

```python
dropdown = page.get_by_label("Country")

# По тексту опции (то, что видит пользователь)
dropdown.select_option(label="United States")

# По атрибуту value
dropdown.select_option(value="US")

# По индексу (с 0)
dropdown.select_option(index=2)

# Несколько (для multi-select)
dropdown.select_option(["Red", "Blue"])
```

**Правило выбора:** `label` — самое читаемое. `value` — если знаешь точное
значение и оно стабильно. `index` — последнее средство.

### Чтение выбранного

```python
# Текущее значение
selected = dropdown.input_value()

# Все опции
options = dropdown.locator("option").all_text_contents()

# Ассерт на выбранную
expect(dropdown).to_have_value("US")
```

---

## Textarea

С точки зрения Playwright — то же, что text input. Те же методы:

```python
textarea = page.get_by_label("Message")
textarea.fill("Hello, this is my multiline\nmessage")
expect(textarea).to_have_value("Hello, this is my multiline\nmessage")
```

Перенос строки — обычный `\n`.

---

## Файловые инпуты — `set_input_files`

Никогда не пиши скрипт, который "кликает Browse и открывает диалог" — не
заработает в headless. Playwright обходит диалог напрямую:

```python
file_input = page.get_by_label("Upload file")
file_input.set_input_files("path/to/file.pdf")

# Несколько файлов
file_input.set_input_files(["file1.png", "file2.png"])

# Очистить
file_input.set_input_files([])

# Из памяти (без файла на диске)
file_input.set_input_files({
    "name": "test.txt",
    "mimeType": "text/plain",
    "buffer": b"file content",
})
```

`set_input_files` работает даже если сам input скрыт (что часто на красивых
UI с кастомным "Choose file" дизайном).

---

## Состояния элементов — все ассерты

| Ассерт                        | Что проверяет                                  |
|-------------------------------|-------------------------------------------------|
| `to_be_visible`               | Видим                                           |
| `to_be_hidden`                | Скрыт                                           |
| `to_be_enabled`               | Активен (можно взаимодействовать)               |
| `to_be_disabled`              | Заблокирован (`disabled` атрибут)               |
| `to_be_editable`              | Можно редактировать (не readonly, не disabled)  |
| `to_be_focused`               | В фокусе                                        |
| `to_be_empty`                 | Пустой (для input/textarea: value = "")         |
| `to_be_checked`               | Чекбокс/radio отмечен                           |
| `to_have_value`               | Значение поля                                   |
| `to_have_text`                | Текст элемента                                  |
| `to_have_attribute`           | Атрибут с заданным значением                    |
| `to_have_count`               | Количество элементов в локаторе                 |

```python
expect(submit_button).to_be_disabled()
expect(email_input).to_be_empty()
expect(form).to_be_visible()
expect(error_message).to_have_text("Email is required")
```

---

## Валидация форм — что и как тестировать

### HTML5-валидация (нативная)

Браузер сам валидирует поля с атрибутами `required`, `type="email"`,
`pattern=`, `min`/`max`. При submit с невалидными данными — браузер показывает
тултип и **не отправляет** форму.

```python
# Проверить, что поле требует email
expect(email_input).to_have_attribute("type", "email")
expect(email_input).to_have_attribute("required", "")

# После некорректного submit — поле помечено
# В разных браузерах ведут себя по-разному, но aria-invalid обычно работает
expect(email_input).to_have_attribute("aria-invalid", "true")
```

### Серверная или кастомная валидация

Сайт показывает сообщения об ошибках текстом — проверяй текст:

```python
submit_button.click()
expect(page.get_by_text("Email is required")).to_be_visible()
expect(page.get_by_text("Password must be at least 8 characters")).to_be_visible()
```

### `validationMessage` (продвинутый)

```python
# Текст валидационного сообщения браузера
message = email_input.evaluate("el => el.validationMessage")
```

Это нативное JS-свойство. Использовать осторожно — тексты разные в Chrome/Firefox.

---

## Паттерны работы с формами

### `register(data: dict)` метод в POM

Вместо длинного списка `fill` в тесте — собери в метод:

```python
class RegisterPage(BasePage):
    PATH = "/auth/register"

    def register(self, data: dict) -> None:
        self.page.get_by_label("First name").fill(data["first_name"])
        self.page.get_by_label("Last name").fill(data["last_name"])
        self.page.get_by_label("Email").fill(data["email"])
        self.page.get_by_label("Password").fill(data["password"])
        self.page.get_by_label("Country").select_option(label=data["country"])
        self.page.get_by_role("button", name="Register").click()
```

В тесте:

```python
def test_register_with_valid_data(page):
    RegisterPage(page).open().register({
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@test.com",
        "password": "Test1234!",
        "country": "United States",
    })
    expect(page).to_have_url("/account")
```

### Тестовые данные не в тесте

`utils/test_data.py`:

```python
VALID_USER = {
    "first_name": "John",
    ...
}
```

Или генерация:

```python
from faker import Faker
fake = Faker()

def generate_user() -> dict:
    return {
        "first_name": fake.first_name(),
        "email": fake.email(),
        ...
    }
```

Faker — стандартная библиотека для генерации фейковых данных. Ставится через
`pip install faker`.

---

## Антипаттерны

### ❌ `.type()` или `press_sequentially` где должен быть `fill`

```python
# ❌ Медленно и нестабильно
page.get_by_label("Email").press_sequentially("user@test.com")

# ✅ Быстро и надёжно
page.get_by_label("Email").fill("user@test.com")
```

`press_sequentially` имеет смысл только для autocomplete и подобных кейсов.

### ❌ `assert` против состояния UI

```python
# ❌ Нет auto-wait, плохая диагностика
assert checkbox.is_checked() == True
assert input.input_value() == "John"

# ✅
expect(checkbox).to_be_checked()
expect(input).to_have_value("John")
```

### ❌ `wait_for_timeout` после `fill` или `click`

```python
# ❌
email_input.fill("test@test.com")
page.wait_for_timeout(2000)
submit_button.click()

# ✅ Никаких ожиданий не нужно
email_input.fill("test@test.com")
submit_button.click()
```

`fill` сам ждёт элемент до 5 секунд. После `click` — `expect` на следующий
шаг сам ждёт.

### ❌ Локаторы через индексы для форм

```python
# ❌
inputs = page.locator("input")
inputs.nth(2).fill("John")

# ✅
page.get_by_label("First name").fill("John")
```

### ❌ Хардкод данных в тесте

```python
# ❌
def test_register(page):
    page.fill("#email", "john@test.com")
    page.fill("#password", "Test1234!")
    ...

# ✅
def test_register(page):
    RegisterPage(page).open().register(VALID_USER)
```

---

## Главные тейкауэи

1. **`get_by_label`** — основной локатор для форм.
2. **`fill()` — в 99% случаев.** `press_sequentially` — только для autocomplete.
3. **`expect(...)` — для UI.** `input_value()` / `get_attribute()` — для данных.
4. **Чекбоксы:** `check`/`uncheck` идемпотентны. Radio: `check` только, `uncheck`
   на radio бесполезен.
5. **Селект:** `select_option(label=)` — самое читаемое.
6. **Файлы:** `set_input_files`, не клики по диалогу.
7. **POM-метод `register(data: dict)`** или `submit_contact(data: dict)` —
   формы инкапсулируются за одним вызовом.
8. **Тестовые данные** — в `utils/test_data.py` или через Faker. Не в тестах.
9. **Никаких** `wait_for_timeout`, `assert` против UI, локаторов по индексу.
