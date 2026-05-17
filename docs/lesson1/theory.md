# Урок 1 — Playwright + pytest: установка и первые тесты

## 1. Что такое Playwright и зачем он

Playwright — это фреймворк от Microsoft для end-to-end тестирования веб-приложений.
Управляет реальным браузером (Chromium, Firefox, WebKit) через DevTools-протокол.

**Чем отличается от Selenium (коротко, на собес):**
- Один API на Chromium / Firefox / WebKit (Selenium = WebDriver на каждый браузер).
- **Auto-waiting** встроен в каждое действие — не надо ставить `time.sleep()` или явные `WebDriverWait`.
- Изолированные **browser contexts** — в одном браузере параллельно несколько "анонимных профилей", куки/localStorage не пересекаются.
- Встроенные tracing, video, screenshots, network mocking.
- Один процесс — нет отдельного драйвера-посредника, отсюда скорость и стабильность.

В Python Playwright поставляется как два пакета:
- `playwright` — сам движок.
- `pytest-playwright` — плагин, который даёт фикстуры (`page`, `browser`, `context`) и CLI-флаги (`--headed`, `--browser`, ...).

---

## 2. Установка (актуально на 2026)

```bash
pip install pytest pytest-playwright
playwright install            # скачивает Chromium, Firefox, WebKit
```

Если нужны только нужные браузеры:
```bash
playwright install chromium   # только хром
```

Обновление:
```bash
pip install -U pytest-playwright playwright
playwright install
```

> Курс показывает `pip install pytest-playwright` — этого мало, так как `pytest` сам не подтянется как обязательная зависимость в некоторых средах. Безопаснее ставить явно: `pip install pytest pytest-playwright`.

---

## 3. Sync vs Async API

Playwright предоставляет **два независимых API**:

| API           | Импорт                            | Когда использовать                              |
|---------------|-----------------------------------|-------------------------------------------------|
| **Sync**      | `from playwright.sync_api import` | Pytest-тесты, обычные скрипты — **наш выбор**.  |
| **Async**     | `from playwright.async_api import`| Если ты пишешь асинхронный сервис (FastAPI, бот) и хочешь дёргать браузер из `async` кода. |

**Правило:** в pytest-проекте всегда берём **sync API**. Плагин `pytest-playwright` фикстуру `page` отдаёт именно из sync API. Если попробуешь смешать sync и async — получишь ошибку event loop.

Async-пример из материалов курса (`test_playwright_async.py`) — рабочий, но для нашего проекта **не нужен**. Async добавляет сложность (event loop, `pytest-asyncio`) без выигрыша в pytest-сценариях.

---

## 4. Главные фикстуры `pytest-playwright`

Когда ты пишешь:

```python
def test_smth(page: Page):
    page.goto(...)
```

— pytest сам создаёт цепочку фикстур:

```
playwright  ──>  browser  ──>  context  ──>  page
(session)        (session)      (function)    (function)
```

| Фикстура   | Scope    | Что это                                                                                        |
|------------|----------|------------------------------------------------------------------------------------------------|
| `playwright` | session | Сам движок Playwright.                                                                         |
| `browser`  | session  | Запущенный браузер (Chromium и т.д.). Один на весь прогон.                                     |
| `context`  | function | **Изолированный профиль** — свои cookies, localStorage, кеш. Новый на каждый тест.             |
| `page`     | function | Вкладка внутри `context`. Новая на каждый тест.                                                |

**Ключевая идея:** изоляция тестов между собой обеспечена бесплатно. Ты залогинился в тесте A — в тесте B про это никто не знает.

Для тонкой настройки контекста (например, viewport, locale, разрешения) переопределяют фикстуру `browser_context_args`:

```python
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "locale": "en-US",
    }
```

Это разберём подробно на следующих уроках, сейчас просто знай, где крутятся настройки.

---

## 5. `expect()` vs `assert` — главное правило

Курс пишет:
```python
expect(page).to_have_url("...")
```

И **никак не объясняет, чем это лучше** простого `assert page.url == "..."`. А разница огромная.

### Почему голый `assert` для UI — плохо

```python
# ПЛОХО
page.click("#submit")
assert page.locator("#success").is_visible()    # элемент ещё не успел появиться → False → флакай тест
```

`assert` срабатывает **мгновенно**, в момент вызова. Если асинхронная UI-операция не успела — тест упадёт ложно.

### Что делает `expect()`

```python
# ХОРОШО
page.click("#submit")
expect(page.locator("#success")).to_be_visible()   # ждёт до 5 сек, перепроверяя
```

`expect()` — **web-first assertion**. Он:
1. Циклически проверяет условие.
2. Ждёт до `timeout` (по умолчанию 5000 мс).
3. Падает, только если за это время условие так и не выполнилось.

**Правило: для всего, что относится к странице/элементам, используй `expect()`. `assert` оставляй только для проверки чистых Python-объектов (числа, словари, ответы API).**

### Самые ходовые web-first ассерты

```python
expect(page).to_have_url(url)
expect(page).to_have_title(title)

expect(locator).to_be_visible()
expect(locator).to_be_hidden()
expect(locator).to_have_text("...")
expect(locator).to_contain_text("...")
expect(locator).to_have_value("...")        # для input
expect(locator).to_have_count(5)            # сколько элементов в локаторе
expect(locator).to_be_enabled()
expect(locator).to_be_disabled()
expect(locator).to_be_checked()
```

Полный список — [Playwright Assertions](https://playwright.dev/python/docs/test-assertions).

---

## 6. Запуск тестов из CLI

Базовое:
```bash
pytest                          # все тесты, headless, chromium
pytest -s -v                    # -s = не глотать print, -v = verbose
pytest tests/ui/test_home.py    # один файл
pytest tests/ui/test_home.py::test_title  # один тест
pytest -k "title"               # все тесты с "title" в имени
pytest -m smoke                 # все тесты с маркером @pytest.mark.smoke
```

Playwright-специфичные флаги (даёт `pytest-playwright`):

| Флаг                                | Что делает                                                                 |
|-------------------------------------|----------------------------------------------------------------------------|
| `--headed`                          | Запустить браузер с UI (по умолчанию headless).                            |
| `--browser chromium`                | Какой браузер. Можно указывать несколько раз.                              |
| `--browser-channel chrome`          | Использовать установленный Chrome/Edge вместо встроенного Chromium.        |
| `--slowmo 500`                      | Замедлить каждое действие на N мс — для глаз во время дебага.              |
| `--device "iPhone 13"`              | Эмулировать устройство.                                                    |
| `--tracing on`                      | Писать trace для каждого теста (мощнейшая штука, см. ниже).                |
| `--tracing retain-on-failure`       | Трейс сохраняется только для упавших тестов — оптимально для CI.           |
| `--video retain-on-failure`         | То же для видео.                                                           |
| `--screenshot only-on-failure`      | То же для скриншотов.                                                      |
| `--output results/`                 | Куда складывать артефакты.                                                 |

Параллельный прогон через `pytest-xdist`:

```bash
pip install pytest-xdist
pytest -n 4         # 4 воркера параллельно
pytest -n auto      # столько воркеров, сколько ядер
```

> Так как у каждого теста свой `context`, параллелизация работает из коробки — тесты не мешают друг другу.

---

## 7. Trace Viewer — обязательно к освоению

Когда тест упал в CI и непонятно почему — открываешь trace и видишь:
- Каждое действие пошагово.
- Скриншот **до и после** каждого шага.
- DOM snapshot — можно тыкнуть в элементы.
- Network log.
- Console log.

Включить:
```bash
pytest --tracing retain-on-failure
```

Открыть:
```bash
playwright show-trace test-results/.../trace.zip
```

На собесе: **умение пользоваться Trace Viewer — большой плюс.** Многие пишут тесты, но не умеют дебажить упавшие.

---

## 8. Структура проекта (закладываем сразу)

```
pet_autotests/
├── conftest.py            # общие фикстуры (browser_context_args и т.п.)
├── pytest.ini             # конфиг pytest: маркеры, опции, addopts
├── requirements.txt       # зависимости
├── .env                   # base_url, креды — никогда не коммитим
├── .env.example           # шаблон, коммитим
├── pages/                 # Page Object Model
│   ├── base_page.py
│   └── home_page.py
├── tests/
│   ├── ui/                # UI-тесты через Playwright
│   └── api/               # API-тесты через httpx/requests
└── utils/                 # хелперы (генераторы данных, форматтеры)
```

**Зачем POM с первого урока:** даже если у нас 2 теста, привычка не писать `page.locator("#submit")` прямо в тесте экономит часы рефакторинга на 50+ тестах. На собесе POM спрашивают всегда.

**Зачем `.env`:** база автотестов = `https://practicesoftwaretesting.com/`, но завтра окружение поменяется. Никаких хардкоженых URL в коде.

---

## 9. Чек-лист понимания урока

- [ ] Понимаю, что pytest-playwright = плагин, дающий фикстуру `page`.
- [ ] Знаю, почему берём sync API.
- [ ] Различаю scope `browser` (session) и `context`/`page` (function).
- [ ] Понимаю, **почему** `expect()` ≠ `assert`, и когда какой использовать.
- [ ] Знаю флаги `--headed`, `--browser`, `--slowmo`, `--tracing`.
- [ ] Понимаю, что параллельный прогон даёт `pytest-xdist`, а изоляцию — context.
- [ ] Слышал про Trace Viewer и зачем он.
