# Шпаргалка — урок 1

## Установка

```bash
pip install pytest pytest-playwright
playwright install            # все браузеры
playwright install chromium   # только хром

pip install -U pytest-playwright playwright   # обновление
```

## Минимальный тест

```python
from playwright.sync_api import Page, expect

def test_home(page: Page):
    page.goto("https://practicesoftwaretesting.com/")
    expect(page).to_have_title("Practice Software Testing - Toolshop - v5.0")
```

## CLI — самое нужное

| Команда                                              | Что делает                          |
|------------------------------------------------------|-------------------------------------|
| `pytest`                                             | Все тесты, headless, chromium       |
| `pytest -s -v`                                       | print не глотать, verbose           |
| `pytest --headed`                                    | Открыть браузер визуально           |
| `pytest --browser firefox`                           | Запуск в Firefox                    |
| `pytest --browser chromium --browser firefox`        | Сразу в двух браузерах              |
| `pytest --slowmo 500`                                | Замедлить на 500 мс/действие        |
| `pytest --tracing retain-on-failure`                 | Трейс упавших тестов                |
| `pytest --video retain-on-failure`                   | Видео упавших тестов                |
| `pytest --screenshot only-on-failure`                | Скриншот при падении                |
| `pytest -k title`                                    | По имени теста                      |
| `pytest -m smoke`                                    | По маркеру                          |
| `pytest path/to/file.py::test_name`                  | Конкретный тест                     |
| `pytest -n auto`                                     | Параллельно (нужен `pytest-xdist`)  |

Открыть трейс:
```bash
playwright show-trace test-results/.../trace.zip
```

## `expect()` vs `assert`

| Случай                          | Что использовать |
|---------------------------------|------------------|
| Свойства страницы и элементов   | `expect(...)`    |
| Чистый Python (числа, dict)     | `assert`         |
| Тело API-ответа (json)          | `assert`         |

`expect()` сам ждёт до 5 сек и перепроверяет — `assert` срабатывает мгновенно.

## Топ-10 web-first ассертов

```python
expect(page).to_have_url(url)
expect(page).to_have_title(title)

expect(loc).to_be_visible()
expect(loc).to_be_hidden()
expect(loc).to_be_enabled()
expect(loc).to_be_disabled()
expect(loc).to_have_text("exact")
expect(loc).to_contain_text("part")
expect(loc).to_have_value("input value")
expect(loc).to_have_count(3)
```

## Фикстуры pytest-playwright

| Фикстура  | Scope    | Что это                       |
|-----------|----------|-------------------------------|
| `playwright` | session | Движок                        |
| `browser`    | session | Один браузер на весь прогон   |
| `context`    | function| Изолированный профиль на тест |
| `page`       | function| Вкладка внутри `context`      |

Кастомизация контекста — через переопределение `browser_context_args` в `conftest.py`.

## Что брать в проект

- Sync API (`from playwright.sync_api import ...`)
- POM с первого теста
- `expect()` для UI, `assert` для не-UI
- `.env` для `BASE_URL`, никаких хардкодов
- `--tracing retain-on-failure` в CI
