# Урок 4 — XPath

## Контекст: где XPath в приоритете локаторов

После уроков 2 и 3 ты знаешь приоритет:

```
get_by_role  →  get_by_label  →  get_by_placeholder  →  get_by_text
              →  get_by_test_id  →  page.locator("css")  →  XPath
```

XPath — **последний** в списке. Это fallback к fallback'у.
Но знать обязательно: на собеседовании спросят, на legacy-проектах встретишь,
и для некоторых задач (навигация по дереву DOM "вверх") у XPath нет аналогов
в CSS.

> **Главное правило 2025:** если первая мысль "сейчас напишу XPath" — остановись
> и проверь, нельзя ли решить через `get_by_*`. В 9 случаях из 10 — можно.

---

## Когда XPath реально нужен

1. **Навигация "вверх" по дереву** — `ancestor::`, `parent::`, `..`. CSS этого
   не умеет (есть `:has()`, но он смотрит "вниз").
2. **Точное совпадение текста с нормализацией пробелов** — `normalize-space()`.
3. **Сложная логика с осями** — "найди input, который сразу после label с
   текстом 'Email'".
4. **Legacy-сайты без ARIA и `data-test`** — где CSS-классы кодгенерированы и
   меняются на каждой сборке.

Во всех остальных случаях — `get_by_*` или CSS.

---

## Absolute vs Relative

### Absolute XPath (никогда не используй)

```
/html/body/div[4]/div[1]/div[1]/div[1]/a/img
```

- Начинается с одного `/`
- Полный путь от корня DOM
- **Сломается** от любой перестановки элементов
- Получается через "Copy → XPath" в DevTools и выглядит "профессионально" — но это самый хрупкий локатор из возможных

### Relative XPath (нормальный)

```
//img[@alt='Tricentis Demo Web Shop']
```

- Начинается с `//` — "ищи где угодно в документе"
- Опирается на атрибуты, а не на структуру
- Устойчив к перестановкам

**Правило:** `//` — всегда. `/` в начале — никогда.

---

## Базовый синтаксис

```
//tagname[@attribute='value']
```

- `//` — поиск где угодно
- `tagname` — имя тега (или `*` — любой)
- `[...]` — фильтр-предикат
- `@attribute` — обращение к атрибуту

```python
page.locator("//input[@id='email']")
page.locator("//button[@type='submit']")
page.locator("//*[@data-test='search-query']")  # любой тег с этим атрибутом
```

> **Кавычки:** XPath требует одного типа внутри, другого снаружи.
> `"//input[@name='q']"` — окей. `'//input[@name="q"]'` — тоже окей.
> Смешать — синтаксическая ошибка.

---

## Условия: `and`, `or`, `not()`

```python
# Несколько атрибутов сразу — два предиката подряд:
page.locator("//input[@type='submit'][@value='Search']")

# То же через and:
page.locator("//input[@type='submit' and @value='Search']")

# Через or — любой из:
page.locator("//button[@name='start' or @name='stop']")

# not — исключение:
page.locator("//input[not(@type='hidden')]")
page.locator("//a[not(@target='_blank')]")
```

`and` и `or` — XPath-операторы внутри `[]`. Не путай с побитовыми операторами
Python — здесь это просто строка.

---

## Функции для атрибутов

### `contains(@attr, 'value')` — подстрока

```python
# Атрибут содержит 'product-' где угодно
page.locator("//*[contains(@data-test, 'product-')]")

# Класс содержит 'btn' (вместо точного матча)
page.locator("//button[contains(@class, 'btn')]")
```

CSS-аналог: `[data-test*='product-']`.

### `starts-with(@attr, 'value')` — начало строки

```python
# data-test начинается с 'product-'
page.locator("//*[starts-with(@data-test, 'product-')]")
```

CSS-аналог: `[data-test^='product-']`.

### Комбинация — для дикой динамики

```python
# id начинается с 'user' И name содержит 'field'
page.locator("//input[starts-with(@id, 'user') and contains(@name, 'field')]")
```

> XPath **не умеет** `ends-with()` в XPath 1.0 (а браузеры поддерживают только 1.0).
> Если нужно "заканчивается на" — пиши через CSS: `[src$='.png']`.

---

## Функции для текста

### `text()` — прямой текст узла

```python
# Кнопка с точным текстом 'Login'
page.locator("//button[text()='Login']")

# Ссылка 'Register'
page.locator("//a[text()='Register']")
```

> ⚠ `text()` — это **прямой** текстовый узел, не вложенный.
> `<button>Login</button>` — `text()='Login'` найдёт.
> `<button><span>Login</span></button>` — **не найдёт**, текст внутри `<span>`.
> Для вложенных — `.` (точка) или `contains(., 'Login')`.

### `contains(text(), 'value')` — подстрока

```python
# Все заголовки, содержащие 'Fiction'
page.locator("//h2[contains(text(), 'Fiction')]")
```

### `normalize-space()` — обрезка пробелов

```html
<button>   Login   </button>
```

```python
# text()='Login' — не найдёт (есть пробелы)
# normalize-space() обрежет крайние пробелы и схлопнет внутренние
page.locator("//button[normalize-space(text())='Login']")

# Краткая форма — normalize-space() без аргументов = текст текущего узла
page.locator("//button[normalize-space()='Login']")
```

Это самая частая засада в XPath: вёрстка содержит пробелы или переносы,
а `text()='X'` про это не знает. Если есть сомнения — используй
`normalize-space()`.

---

## Позиция: `[N]`, `position()`, `last()`

### `[N]` — N-й среди братьев

```python
# Второй <li> внутри <ul>
page.locator("//ul/li[2]")

# Первый <p> внутри каждого <div>
page.locator("//div/p[1]")
```

### `last()` — последний

```python
# Последний <li> в меню FOLLOW US
page.locator("//div[@class='column follow-us']//li[last()]")
```

### `position()` — позиция

```python
# То же, что [2]:
page.locator("//li[position()=2]")

# Все, кроме первого:
page.locator("//li[position()>1]")
```

### `(//...)[N]` — N-й среди всех найденных

**Очень важно знать разницу:**

```python
# //input[1] — каждый input, который ПЕРВЫЙ среди своих братьев (может быть много)
page.locator("//input[1]")

# (//input)[1] — ПЕРВЫЙ input во всём документе (всегда один)
page.locator("(//input)[1]")
```

Скобки группируют выражение, и `[N]` применяется к результату всей выборки,
а не к каждому братскому набору отдельно.

---

## Оси (axes) — главное преимущество XPath

Здесь XPath обходит CSS. CSS умеет идти "вниз" (потомки) и "вбок" (сиблинги
после), но не умеет идти "вверх" к родителям. XPath умеет всё.

Синтаксис оси:

```
//tag/axis::filter
```

### `ancestor::` — все предки вверх до корня

```python
# Найти карточку товара, в которой есть цена $9.99
page.locator("//*[text()='$9.99']/ancestor::a[@data-test]")
```

В CSS такого нет.

### `parent::` или `..` — прямой родитель

```python
# Родитель элемента с этим id
page.locator("//*[@id='email']/parent::div")

# То же короче:
page.locator("//*[@id='email']/..")
```

### `child::` или `/` — прямые потомки

```python
# Прямые <li>-потомки <ul id='menu'>
page.locator("//ul[@id='menu']/child::li")

# То же короче:
page.locator("//ul[@id='menu']/li")
```

### `descendant::` или `//` — все потомки

```python
# Все <a> где-то внутри <div id='main'>
page.locator("//div[@id='main']/descendant::a")

# То же короче:
page.locator("//div[@id='main']//a")
```

### `following-sibling::` — соседи **после** на том же уровне

```html
<label>Email</label>
<input id="email">
<small>hint</small>
```

```python
# input сразу после label 'Email'
page.locator("//label[text()='Email']/following-sibling::input")

# CSS-аналог через `+`: label + input — работает только для прямого соседа.
# XPath ищет всех сиблингов после.
```

### `preceding-sibling::` — соседи **до** на том же уровне

```python
# label сразу перед input
page.locator("//input[@id='email']/preceding-sibling::label")
```

В CSS такого нет (`:has-prev` в спеке нет).

### `following::` — все элементы после в порядке документа

```python
# Любой input где-то после label 'Email' (не обязательно сосед)
page.locator("//label[text()='Email']/following::input[1]")
```

`[1]` здесь — первый из найденных, ближайший.

### `preceding::` — все элементы до

```python
# Ближайший заголовок перед текущим элементом
page.locator("//input[@id='email']/preceding::h2[1]")
```

### `self::` — сам узел

Редко полезно, но бывает:

```python
# Этот же элемент, если он div с классом sale
page.locator("//*[@id='card-1']/self::div[contains(@class,'sale')]")
```

### Кратко все оси

| Ось                  | Что выбирает                            |
|----------------------|------------------------------------------|
| `ancestor`           | Все предки                               |
| `parent` / `..`      | Прямой родитель                          |
| `descendant` / `//`  | Все потомки                              |
| `child` / `/`        | Прямые потомки                           |
| `following`          | Все элементы после в документе           |
| `preceding`          | Все элементы до в документе              |
| `following-sibling`  | Соседи после на том же уровне            |
| `preceding-sibling`  | Соседи до на том же уровне               |
| `self`               | Текущий узел                             |

---

## Wildcard `*`

`*` — любой тег.

```python
# Любой элемент с этим атрибутом
page.locator("//*[@data-test='search-query']")

# Любой потомок div
page.locator("//div/*")
```

Полезно, когда атрибут уникален и тег может меняться. Но обычно лучше явно
указывать тег — это быстрее и читаемее.

---

## XPath vs CSS — таблица соответствий

| Задача                              | CSS                              | XPath                                        |
|-------------------------------------|----------------------------------|----------------------------------------------|
| По тегу                              | `button`                         | `//button`                                   |
| По id                                | `#login`                         | `//*[@id='login']`                           |
| По классу                            | `.btn`                           | `//*[contains(@class,'btn')]`                |
| По атрибуту                          | `[name='q']`                     | `//*[@name='q']`                             |
| Начинается с                         | `[id^='user']`                   | `//*[starts-with(@id,'user')]`               |
| Содержит                              | `[class*='primary']`             | `//*[contains(@class,'primary')]`            |
| Заканчивается на                     | `[src$='.png']`                  | — (нет в XPath 1.0)                          |
| Прямой ребёнок                       | `ul > li`                        | `//ul/li`                                    |
| Любой потомок                        | `ul li`                          | `//ul//li`                                   |
| Сосед сразу после                    | `h2 + p`                         | `//h2/following-sibling::p[1]`               |
| Любой сосед после                    | `h2 ~ p`                         | `//h2/following-sibling::p`                  |
| **Сосед до**                         | — (нет)                          | `//input/preceding-sibling::label`           |
| **Родитель**                         | — (нет)                          | `//*[@id='x']/parent::div` или `..`          |
| **Предки**                           | — (нет)                          | `//*[@id='x']/ancestor::section`             |
| N-й среди братьев                    | `:nth-child(2)`                  | `//li[2]`                                    |
| N-й среди всех найденных             | `:nth-match()` (Playwright)      | `(//input)[2]`                               |
| По тексту                             | `:has-text('X')` (Playwright)    | `//*[text()='X']`                            |
| По части текста                      | `:has-text('X')` (Playwright)    | `//*[contains(text(),'X')]`                  |
| Без атрибута                         | `:not([hidden])`                 | `//*[not(@hidden)]`                          |

**Где XPath сильнее CSS:** `parent`, `ancestor`, `preceding-sibling`, нормализация пробелов.

**Где CSS сильнее XPath:** проще, читаемее, быстрее в браузере, нативная поддержка
без парсинга.

---

## XPath vs Playwright API

Многое из того, что в XPath занимает строку, в Playwright API делается через
методы локатора:

| Задача                                | XPath                                      | Playwright API                                       |
|---------------------------------------|--------------------------------------------|-------------------------------------------------------|
| По роли                                | `//button` + проверка имени                | `get_by_role("button", name="Login")`                |
| По label                               | `//label/following::input[1]`              | `get_by_label("Email")`                              |
| По тексту                              | `//*[text()='Hammer']`                     | `get_by_text("Hammer")`                              |
| По placeholder                         | `//input[@placeholder='Search']`           | `get_by_placeholder("Search")`                       |
| N-й                                    | `(//tag)[N+1]`                             | `locator(...).nth(N)`                                |
| Фильтр по тексту                       | `//card[contains(.,'Hammer')]`             | `locator("...").filter(has_text="Hammer")`           |
| Фильтр по дочернему элементу           | `//card[.//price]`                         | `locator("...").filter(has=...)`                     |
| Родитель                                | `//*[@id='x']/ancestor::form`              | — (нет прямого API, нужно XPath или `:has()` инверсно)|

**Главный вывод:** там, где XPath демонстрирует "силу" — это в 80% случаев
**проще** через Playwright API. XPath остаётся для пары узких задач:
поиск родителя, нормализация пробелов, сложные оси.

---

## Антипаттерны

### ❌ Absolute XPath

```python
page.locator("/html/body/div[4]/div/section/div[2]/h1")
```

Сломается от любой перестановки. Всегда `//`, никогда `/` в начале.

### ❌ Цепляться за позицию там, где есть атрибут

```python
# Плохо
page.locator("(//button)[5]")

# Хорошо
page.locator("//button[@data-test='submit']")
```

Позиция меняется при добавлении любой кнопки выше. Атрибут — стабилен.

### ❌ XPath там, где работает get_by_role

```python
# Плохо
page.locator("//button[text()='Login']").click()

# Хорошо
page.get_by_role("button", name="Login").click()
```

`get_by_role` — устойчив к переводу, к смене тега (`<button>` ↔ `<a role="button">`),
и читается как сценарий.

### ❌ `text_content()` + `assert`

```python
title = page.locator("//h1").text_content()
assert title == "Hammer"
```

Нет auto-wait, упадёт при асинхронном рендере. Правильно:

```python
expect(page.locator("//h1")).to_have_text("Hammer")
```

### ❌ `wait_for_timeout` после XPath

```python
page.locator("//button[@data-test='save']").click()
page.wait_for_timeout(3000)  # ❌
expect(page.locator("//div[@class='toast']")).to_be_visible()
```

`expect` сам ждёт до 5 секунд. Никаких sleep'ов.

### ❌ Локатор по сгенерированному id

```python
# id типа "ng-1234567" или "react-component-abc"
page.locator("//*[@id='ng-1234567']")
```

Меняется на каждой сборке. Используй `data-test`, ARIA, или текст.

---

## Главные тейкауэи

1. **XPath — последний выбор**, не первый. `get_by_*` → CSS → XPath.
2. **Только relative XPath** (`//`). Никогда не пиши absolute (`/html/...`).
3. **Главная сила XPath — оси**: `ancestor`, `parent`/`..`, `following-sibling`,
   `preceding-sibling`. Это то, чего нет в CSS.
4. **`normalize-space()`** — против ловушек с пробелами в `text()`.
5. **`//tag[1]` ≠ `(//tag)[1]`** — знай разницу для собеса.
6. **80% "сильного" XPath решается проще** через `get_by_role`, `.filter()`,
   `.nth()`.
7. **Никаких** absolute paths, хардкоженных индексов, `wait_for_timeout`,
   `text_content()` + `assert`.
