# Шпаргалка — урок 3

## Базовый синтаксис

| Цель                          | Селектор                |
|-------------------------------|-------------------------|
| Тег                           | `button`                |
| ID                            | `#login` или `button#login` |
| Класс                         | `.btn` или `button.btn` |
| Атрибут (наличие)             | `input[required]`       |
| Атрибут (значение)            | `[name="email"]`        |
| Все элементы                  | `*`                     |
| Несколько селекторов (OR)     | `h1, h2, h3`            |

---

## Атрибутные селекторы

| Оператор | Что значит                      | Пример                            |
|----------|----------------------------------|-----------------------------------|
| `=`      | Точное совпадение               | `[type="email"]`                  |
| `^=`     | Начинается с                     | `[data-test^="product-"]`         |
| `$=`     | Заканчивается на                | `[src$=".png"]`                   |
| `*=`     | Содержит подстроку              | `[class*="primary"]`              |
| `~=`     | Содержит слово (через пробел)    | `[class~="active"]`               |
| `\|=`    | Точно `val` или `val-...`        | `[lang\|="en"]`                   |

---

## Комбинаторы

```
A B    descendant       — B где-то внутри A
A > B  child             — B прямой ребёнок A
A + B  adjacent sibling  — B сразу после A
A ~ B  general sibling   — любой B после A на том же уровне
```

```python
page.locator(".card button")     # любая кнопка внутри карточки
page.locator(".card > button")   # только прямой ребёнок
page.locator("h2 + p")           # параграф сразу после h2
page.locator("h2 ~ p")           # все параграфы после h2
```

---

## Псевдоклассы позиции

| Селектор              | Что выбирает                         |
|-----------------------|--------------------------------------|
| `:first-child`        | Первый ребёнок родителя              |
| `:last-child`         | Последний ребёнок                    |
| `:nth-child(n)`       | N-й ребёнок (с 1)                    |
| `:nth-child(odd)`     | Нечётные                             |
| `:nth-child(even)`    | Чётные                               |
| `:nth-child(3n)`      | Каждый третий                        |
| `:nth-child(-n+3)`    | Первые три                           |
| `:first-of-type`      | Первый элемент СВОЕГО ТЕГА           |
| `:nth-of-type(n)`     | N-й элемент своего тега              |

### `:nth-child` vs `:nth-of-type` — запомнить

```html
<div>
  <h2>Title</h2>     ← :first-child  И  h2:first-of-type
  <p>Para 1</p>      ← :nth-child(2) НО p:first-of-type
  <p>Para 2</p>      ← :nth-child(3) И  p:nth-of-type(2)
</div>
```

`p:nth-child(2)` **НЕ найдёт** "Para 1", потому что ребёнок №2 — это `<h2>`.

---

## Логика

| Селектор        | Что значит                          | Пример                              |
|-----------------|--------------------------------------|-------------------------------------|
| `:not(X)`       | Всё, кроме X                         | `a:not([target='_blank'])`          |
| `:has(X)`       | Элемент, внутри которого есть X      | `.card:has(.price)`                 |
| `:not(:has(X))` | Без X внутри                         | `.card:not(:has(.price))`           |

---

## Playwright-расширения

| Селектор                | Что делает                               |
|-------------------------|------------------------------------------|
| `:visible`              | Только видимые                           |
| `:has-text("text")`     | Содержит текст где-то внутри             |
| `:text("text")`         | Точное совпадение текста                 |
| `:text-is("text")`      | То же, что `:text`                       |
| `>>`                    | Chaining в одну строку                   |
| `:nth-match(sel, N)`    | N-й найденный (с 1)                       |
| `:scope`                | Текущий root в `.locator()`              |

```python
page.locator(".modal:visible")
page.locator(".product:has-text('Hammer')")
page.locator("nav >> a.logout")
```

---

## CSS vs Playwright API — что когда

| Задача                                  | Playwright API                  | CSS                                   |
|-----------------------------------------|----------------------------------|---------------------------------------|
| 3-я карточка в сетке                    | `.nth(2)`                        | `:nth-child(3)`                       |
| Карточка с текстом "Hammer"             | `.filter(has_text="Hammer")`     | `:has-text('Hammer')`                 |
| Карточка с дочерней кнопкой             | `.filter(has=...)`               | `:has(button)`                        |
| Карточка БЕЗ кнопки                     | `.filter(has_not=...)`           | `:not(:has(button))`                  |
| Видимые элементы                        | (по умолчанию `expect` ждёт)     | `:visible`                            |
| Цепочка                                  | `.locator().locator()`           | `>>`                                  |

**Выбирай Playwright API** — он явный и читается лучше.
**Используй CSS** — когда выражение не помещается в API.

---

## Антипаттерны

| ❌                                              | ✅                                            |
|------------------------------------------------|----------------------------------------------|
| `html > body > div > div > h2`                 | `h2` или `[data-test='page-title']`          |
| `.btn.btn-primary.mt-3.px-4`                   | `[data-test='submit-btn']`                   |
| `print(loc.text_content())`                    | `expect(loc).to_have_text(...)`              |
| `assert loc.text_content() == "X"`             | `expect(loc).to_have_text("X")`              |
| `time.sleep(2)` или `wait_for_timeout`         | ничего — `expect` ждёт сам                   |
| `page.query_selector(...)`                     | `page.locator(...)`                          |
