# Урок 3 — CSS-селекторы

## Контекст: где CSS вообще нужен

После урока 2 ты знаешь приоритет локаторов:

```
get_by_role  →  get_by_label  →  get_by_placeholder  →  get_by_text
              →  get_by_test_id  →  page.locator("css")  →  XPath
```

CSS — это **fallback**, когда `get_by_*` не подходит:

- Нужно выбрать N-ый элемент в сетке (карточка номер 3)
- Нужен сложный комбинатор: "цена внутри карточки, в которой есть `Hammer`"
- На сайте нет ARIA-ролей и `data-test`, всё держится на классах
- Нужна фильтрация по нескольким атрибутам сразу

CSS **знать обязательно**. Но если первая мысль "напишу CSS-селектор" — сначала
проверь, нет ли `get_by_role` или `get_by_test_id`. CSS более хрупкий: при
переименовании класса локатор сломается.

---

## Базовый синтаксис

| Что находит              | Селектор                       |
|--------------------------|--------------------------------|
| Все `<button>`           | `button`                       |
| Элемент с `id="login"`   | `#login` или `button#login`    |
| Элементы с `class="btn"` | `.btn` или `button.btn`        |
| Любой элемент            | `*`                            |
| С атрибутом `name="q"`   | `[name="q"]`                   |
| С тегом и атрибутом      | `input[type="email"]`          |

В Playwright:

```python
page.locator("button#login")
page.locator(".product-card")
page.locator("input[type='email']")
```

> **Кавычки в значениях:** в Python используй одинарные внутри двойных
> (или наоборот) — чтобы не экранировать.
> `"input[name='q']"` — окей. `'input[name="q"]'` — тоже окей.

---

## Атрибутные селекторы (важно!)

Это **самая практичная** часть CSS для тестов:

| Селектор             | Что делает                          | Пример                                          |
|----------------------|--------------------------------------|-------------------------------------------------|
| `[attr="val"]`       | Точное совпадение                   | `a[href="/login"]`                              |
| `[attr^="val"]`      | Начинается с                         | `a[href^="/products"]` — `/products`, `/products/42` |
| `[attr$="val"]`      | Заканчивается на                    | `img[src$=".png"]`                              |
| `[attr*="val"]`      | Содержит                             | `[class*="product"]`                            |
| `[attr~="val"]`      | Слово в списке (через пробел)        | `[class~="active"]` — найдёт `class="btn active"`|
| `[attr\|="val"]`     | Точно `val` или `val-...`            | `[lang\|="en"]` — `en`, `en-US`                 |
| `[attr]`             | Просто наличие атрибута              | `input[required]`                                |

### Когда что использовать

- `^=` — для динамических `id`/`data-test` с префиксом: `[data-test^="product-"]`
- `*=` — когда классов несколько и порядок не гарантирован: `[class*="product-card"]`
- `$=` — для расширений файлов: `[src$=".jpg"]`
- `~=` — для класса в списке (но обычно `.class` лучше)

> ⚠ `[class="btn primary"]` — точное совпадение **всей строки**.
> Если на элементе `class="btn primary mt-2"` — не найдёт.
> Используй `.btn.primary` или `[class*="primary"]`.

---

## Комбинаторы — связь между элементами

Это место, где CSS обходит `get_by_*`. Четыре оператора:

| Комбинатор | Имя              | Что значит                                           |
|------------|------------------|------------------------------------------------------|
| ` ` (пробел) | descendant      | Элемент **где-то внутри** другого                     |
| `>`        | child            | Элемент — **прямой** ребёнок                          |
| `+`        | adjacent sibling | Элемент **сразу после** другого (на том же уровне)    |
| `~`        | general sibling  | Любой элемент **после** другого (на том же уровне)    |

### Схема

```html
<div class="card">                    ← .card
  <header>                            ← .card > header  и  .card header
    <h2>Title</h2>                    ← .card > header > h2  и  .card h2
  </header>
  <p>Description</p>                  ← header + p   (сразу после header)
  <p>Note</p>                         ← header ~ p   (любой p после header)
  <a href="...">Buy</a>               ← header ~ a
</div>
```

### Реальные примеры

```python
# Любой <button> внутри карточки (сколько бы ни было вложено)
page.locator(".card button")

# Только прямой <button> карточки
page.locator(".card > button")

# Цена сразу после названия товара
page.locator(".product-name + .product-price")

# Все элементы после h2 в той же секции
page.locator("h2 ~ *")
```

---

## Псевдоклассы позиции

### `:first-child`, `:last-child`, `:nth-child(n)`

Выбирают элемент по позиции среди **всех** братьев.

```html
<ul>
  <li>A</li>      ← :first-child, :nth-child(1)
  <li>B</li>      ← :nth-child(2)
  <li>C</li>      ← :nth-child(3), :last-child
</ul>
```

```python
page.locator("ul > li:first-child")
page.locator("ul > li:nth-child(2)")
page.locator("ul > li:last-child")
```

> 🚨 **Нумерация с 1**, не с 0! Это в CSS, не в Python.
> В Playwright `.nth(0)` = `:nth-child(1)`.

### `:nth-of-type(n)` — частая засада на собесе

Главное отличие от `:nth-child`:
- `:nth-child(2)` — "второй ребёнок родителя, **если он этого тега**"
- `:nth-of-type(2)` — "второй элемент **этого тега** среди братьев"

```html
<div>
  <h2>Заголовок</h2>      ← :first-child  и  h2:first-of-type
  <p>Первый абзац</p>     ← :nth-child(2)  но  p:first-of-type
  <p>Второй абзац</p>     ← :nth-child(3)  и  p:nth-of-type(2)
</div>
```

`p:nth-child(2)` **не найдёт первый `<p>`**, потому что второй ребёнок —
это `<h2>`, не `<p>`. А `p:first-of-type` найдёт.

**Правило:** если тебе важна позиция конкретного тега — `:nth-of-type`.
Если важна позиция в списке однородных — `:nth-child`.

### Формулы в `:nth-child`

```css
:nth-child(odd)        /* 1, 3, 5, ... */
:nth-child(even)       /* 2, 4, 6, ... */
:nth-child(3n)         /* каждый третий: 3, 6, 9 */
:nth-child(3n+1)       /* 1, 4, 7, ... */
:nth-child(-n+3)       /* первые три: 1, 2, 3 */
```

```python
page.locator(".product:nth-child(odd)")     # все нечётные карточки
page.locator(".product:nth-child(-n+5)")    # первые 5
```

---

## `:not()` — исключение

```python
# Все товары, кроме "out of stock"
page.locator(".product:not(.out-of-stock)")

# Все ссылки, кроме внешних
page.locator("a:not([target='_blank'])")

# Цепочка :not()
page.locator("p:not(.muted):not(.hidden)")
```

---

## `:has()` — самый мощный селектор

`:has()` отвечает на вопрос: **"элемент, ВНУТРИ которого есть..."**

Раньше это умел только XPath. Теперь поддерживается современным CSS, и
Playwright прекрасно с ним работает.

```python
# Карточка, в которой есть кнопка "Add to cart"
page.locator(".product:has(button.add-to-cart)")

# Карточка БЕЗ цены
page.locator(".product:not(:has(.price))")

# Строка таблицы, содержащая ячейку с текстом
page.locator("tr:has(td:has-text('Hammer'))")
```

> ⚠ В Playwright есть **два способа** сделать то же самое:
>
> ```python
> # Через CSS :has
> page.locator(".product:has(.price)")
>
> # Через .filter() из урока 2
> page.locator(".product").filter(has=page.locator(".price"))
> ```
>
> Оба валидны. `.filter()` читается лучше в длинных цепочках, `:has()` —
> в одной строке. Выбирай по контексту.

---

## Playwright-специфичные расширения CSS

Playwright добавляет свои псевдоклассы поверх стандартного CSS:

### `:visible`

Только видимые элементы (не `display:none`, не `visibility:hidden`):

```python
page.locator(".modal:visible")  # открытое модальное окно
```

### `:has-text(text)`

Аналог `.filter(has_text=...)` в одной строке:

```python
page.locator(".product:has-text('Hammer')")
page.locator("button:has-text('Add')")
```

> ⚠ Это **не то же самое**, что `get_by_text("Hammer")` —
> `:has-text()` ищет элементы, **содержащие** этот текст где-то внутри.

### `>>` — chaining в одну строку

```python
# То же, что .locator(".sidebar").locator("a.logout")
page.locator(".sidebar >> a.logout")
```

Используй умеренно — обычно `.locator()` чейнингом читается лучше.

### `:nth-match(selector, n)`

Когда `:nth-child` не работает (родители разные), а нужен N-й по порядку:

```python
# Третья кнопка "Add to cart" на странице, неважно где она
page.locator(":nth-match(button.add-to-cart, 3)")
```

Альтернатива через Playwright-объект — `.nth(2)`:

```python
page.locator("button.add-to-cart").nth(2)
```

Второй вариант предпочтительнее — он явный.

### `:scope`

Для текущего корня в `.locator()`:

```python
card = page.locator(".card").first
# Только если сама карточка имеет класс sale, а не её дети
card.locator(":scope.sale")
```

---

## Антипаттерны в CSS-селекторах

### ❌ Абсолютные пути

```python
page.locator("html > body > div > div > main > section > div > h2")
```

Сломается от любой перестановки. Всегда используй относительные.

### ❌ Цепляться за классы фреймворков

```python
# Bootstrap, Tailwind — эти классы меняются при обновлении
page.locator(".btn.btn-primary.mt-3.px-4")
```

Лучше: `data-test`, ARIA, или семантический CSS-селектор по структуре.

### ❌ `text_content()` + `assert`

```python
# Так делает автор курса
title = page.locator(".product-name").text_content()
assert title == "Hammer"
```

Проблемы:
- Нет auto-wait, упадёт если элемент рендерится с задержкой
- Не покажет полезную диагностику при падении

```python
# Правильно
expect(page.locator(".product-name")).to_have_text("Hammer")
```

### ❌ `print(text_content())` для проверки

```python
print("Product name:", page.locator(".product-name").text_content())
```

`print` — это не тест. Используй `expect`. Если реально нужно посмотреть
значение — поставь брейкпоинт или `PWDEBUG=1`.

### ❌ `wait_for_timeout(5000)` после CSS

```python
page.locator(".product").click()
page.wait_for_timeout(5000)  # ❌ зачем?
expect(page.locator(".cart-count")).to_have_text("1")
```

`expect` сам ждёт. Из урока 2: никаких sleep'ов.

---

## Главные тейкауэи

1. **CSS — это fallback**, не первый выбор. Сначала `get_by_*`.
2. **Атрибутные селекторы** — самая практичная часть CSS (`^=`, `*=`).
3. **Combinators** (` `, `>`, `+`, `~`) — для отношений между элементами.
4. **`:nth-child` ≠ `:nth-of-type`** — знай разницу для собеса.
5. **`:has()`** — современная альтернатива XPath. Используй вместо длинных
   родительских цепочек.
6. **Playwright-расширения** (`:visible`, `:has-text`, `>>`) — мощно, но не
   увлекайся: `.filter()`/`.nth()` обычно читается лучше.
7. **Никаких** `print` и `wait_for_timeout` — auto-wait + `expect` решают всё.
