# CI Setup — GitHub + GitHub Actions

## Зачем CI для QA Automation проекта

В реальных командах тесты не запускают руками перед каждым деплоем.
CI (Continuous Integration) делает это автоматически при каждом коммите.

Что это даёт лично тебе на собесе:
- GitHub репозиторий с зелёным badge — видно сразу, что тесты работают
- Артефакты (трейсы, скриншоты) хранятся в истории запусков
- Ты можешь сказать: "у нас настроен CI, тесты гоняются на каждый push"
- Это отличает проект от "папки с файлами" в глазах нанимающего

---

## GitHub Actions — ключевые понятия

```
Репозиторий
└── .github/
    └── workflows/
        └── tests.yml      ← файл описания workflow
```

| Понятие      | Что это                                                          |
|--------------|------------------------------------------------------------------|
| **Workflow** | Весь сценарий: "при пуше запусти тесты"                          |
| **Trigger**  | Событие, которое запускает workflow (push, PR, schedule)         |
| **Job**      | Группа шагов, выполняется на одном runner                        |
| **Step**     | Один конкретный шаг внутри job (checkout, pip install, pytest)   |
| **Runner**   | Виртуальная машина, где выполняется job (ubuntu-latest)          |
| **Artifact** | Файл, который сохраняется после прогона (трейсы, скриншоты)      |
| **Matrix**   | Запустить один job несколько раз с разными параметрами           |
| **Secret**   | Переменная окружения, скрытая от логов (пароли, токены, BASE_URL)|

---

## Готовый workflow для нашего проекта

Файл: `.github/workflows/tests.yml`

```yaml
name: Playwright Tests

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      fail-fast: false        # продолжать матрицу даже если один браузер упал
      matrix:
        browser: [chromium, firefox]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip            # кешируем pip чтобы не скачивать каждый раз

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Install Playwright browsers
        run: playwright install ${{ matrix.browser }} --with-deps
        # --with-deps устанавливает системные зависимости (шрифты, libglib и т.д.)
        # на ubuntu-latest они не установлены по умолчанию

      - name: Run tests
        run: pytest -v --browser ${{ matrix.browser }}
        env:
          BASE_URL: ${{ secrets.BASE_URL }}
          # если секрет не задан — utils/config.py использует дефолт из кода

      - name: Upload test artifacts
        if: failure()           # загружать только если тесты упали
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.browser }}
          path: test-results/
          retention-days: 7     # хранить 7 дней, потом удалить
```

### Разбор ключевых решений

**`fail-fast: false`** — без этого если chromium упал, firefox не запустится вообще.
Нам важно видеть результаты по всем браузерам.

**`playwright install ${{ matrix.browser }} --with-deps`** — устанавливаем только
нужный браузер (не все три) + его системные зависимости. На `ubuntu-latest` нет
libglib2.0, libatk и т.д. — `--with-deps` ставит их автоматически. Без этого
Playwright не запустится.

**`if: failure()`** — загружаем артефакты только при падении. Если всё зелёное,
трейсы не нужны и не занимают место.

**`env: BASE_URL: ${{ secrets.BASE_URL }}`** — переменная из GitHub Secrets.
Если её не задать, `utils/config.py` возьмёт дефолтное значение
`"https://practicesoftwaretesting.com"` — для нашего проекта это нормально,
сайт публичный.

---

## Как смотреть результаты

После прогона:
```
GitHub → репозиторий → Actions → выбери workflow run
```

- Зелёный ✓ — всё прошло
- Красный ✗ — есть падения → скачай артефакт `test-results-chromium.zip`
- Внутри ZIP — `trace.zip` для каждого упавшего теста

Открыть трейс локально:
```bash
playwright show-trace test-results/.../trace.zip
```

---

## Status Badge в README

Добавь в `README.md` (создай его если нет):

```markdown
# Pet Autotests

[![Playwright Tests](https://github.com/ВАШ_АККАУНТ/ВАШ_РЕПО/actions/workflows/tests.yml/badge.svg)](https://github.com/ВАШ_АККАУНТ/ВАШ_РЕПО/actions/workflows/tests.yml)
```

URL берётся прямо из вкладки Actions → выбери workflow → "Create status badge".

---

## Секреты (если понадобятся)

Для нашего проекта `BASE_URL` — публичный сайт, секретить необязательно.
Но паттерн полезно знать для будущих проектов с реальным staging URL.

```
GitHub → репозиторий → Settings → Secrets and variables → Actions → New secret
```

Имя: `BASE_URL`, значение: `https://practicesoftwaretesting.com`

В workflow обращаешься через `${{ secrets.BASE_URL }}`.
В логах GitHub Actions значение будет скрыто как `***`.

---

## Оптимизация — запускать только при изменении тестов

Если не хочешь гонять тесты при правках `README.md`:

```yaml
on:
  push:
    branches: [main, master]
    paths:
      - "tests/**"
      - "pages/**"
      - "utils/**"
      - "conftest.py"
      - "pytest.ini"
      - "requirements.txt"
```

---

## Порядок действий (пошагово)

1. Создать репозиторий на GitHub (Public, без README — он создаётся локально)
2. Инициализировать git локально и связать с remote:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: lesson 1 done"
   git branch -M main
   git remote add origin https://github.com/ВАШ_АККАУНТ/ВАШ_РЕПО.git
   git push -u origin main
   ```
3. Создать `.github/workflows/tests.yml` с содержимым выше
4. `git add .github && git commit -m "ci: add GitHub Actions workflow" && git push`
5. Открыть вкладку Actions в репозитории — увидишь запущенный workflow
6. Добавить badge в README, запушить

После этого: каждый `git push` → автоматический прогон тестов.

---

## Что НЕ пушить

Убедись что `.gitignore` содержит:
```
.env
.venv/
test-results/
playwright-report/
__pycache__/
.pytest_cache/
```

`.env` с реальными данными — **никогда** не в git. В CI используй Secrets.
