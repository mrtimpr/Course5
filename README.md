# Habit Tracker API

Самостоятельный backend-проект для SPA: пользователи создают полезные и
приятные привычки, получают напоминания в Telegram и могут публиковать
привычки для общего просмотра.

Проект запускается на Windows **без Docker, Redis, PostgreSQL и RabbitMQ**.
По умолчанию используются SQLite и локальная файловая очередь Celery.

## Реализовано

- регистрация и JWT-авторизация по email;
- CRUD только для привычек текущего пользователя;
- отдельный read-only список публичных привычек;
- limit/offset-пагинация с `default_limit=5` и полями `count`, `next`,
  `previous`, `results`;
- все правила валидации из задания;
- CORS через `django-cors-headers`, источники фронтенда задаются в `.env`;
- Celery + Celery Beat без внешнего брокера: локальная файловая очередь;
- Telegram Bot API и защита от повторных сообщений одной привычки за день;
- OpenAPI-схема, Swagger UI и ReDoc;
- Ruff-конфигурация для контроля PEP 8.

## Структура

```text
config/              настройки Django, Celery, корневые URL
users/               custom User, регистрация, профиль
habits/              привычки, валидация, CRUD, пагинация, Celery-задача
telegram_bot/        адаптер Telegram Bot API
tests/               API, валидаторы, Telegram и задачи
scripts/             PowerShell-скрипты для Windows
```

## Быстрый запуск в Windows PowerShell

### 1. Открыть PowerShell в папке проекта

```powershell
cd "C:\Users\<ваш_пользователь>\Desktop\habit_tracker_backend"
```

### 2. Выполнить первичную настройку

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\bootstrap_windows.ps1
```

Скрипт самостоятельно создаёт виртуальное окружение, устанавливает
зависимости, копирует `.env.template` в `.env`, создаёт миграции и применяет
их к локальной базе `db.sqlite3`.

### 3. Запустить API

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

API доступно по адресу `http://127.0.0.1:8000/`.

### 4. Запустить Telegram-напоминания

Откройте **два новых** окна PowerShell в папке проекта.

Первое окно — Celery Worker:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\run_worker_windows.ps1
```

Второе окно — Celery Beat:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\run_beat_windows.ps1
```

Celery Beat ставит задачу проверки напоминаний в очередь раз в минуту.
Worker принимает задачу из локальной папки `.celery/` и запускает отправку
уведомлений.

## Ручной запуск без скриптов

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.template .env
python manage.py makemigrations users habits
python manage.py migrate
python manage.py check
python manage.py runserver
```

Для Worker и Beat после активации окружения:

```powershell
celery -A config worker -l INFO --pool=solo
celery -A config beat -l INFO
```

Параметр `--pool=solo` обязателен для Windows.

## `.env`

После копирования `.env.template` измените минимум следующие значения:

```env
SECRET_KEY=ваш_длинный_секретный_ключ
TELEGRAM_BOT_TOKEN=токен_от_BotFather
```

`DATABASE_URL=sqlite:///db.sqlite3` и `CELERY_BROKER_URL=filesystem://`
уже настроены для локального запуска. Никакие контейнеры не требуются.

## Telegram

1. Создайте бота через BotFather и внесите токен в `TELEGRAM_BOT_TOKEN`.
2. Пользователь должен открыть чат с ботом и нажать `/start`.
3. Укажите `telegram_chat_id` при регистрации или через `PATCH /api/users/me/`.
4. Создайте привычку с временем на одну-две минуты позже текущего времени.
5. Worker и Beat отправят напоминание, когда наступит указанная минута.

Без `telegram_chat_id` привычки сохраняются, но уведомления не отправляются.

## Эндпоинты

| Метод | URL | Доступ |
|---|---|---|
| POST | `/api/users/register/` | Все |
| POST | `/api/users/token/` | Все |
| POST | `/api/users/token/refresh/` | Все |
| GET, PATCH | `/api/users/me/` | Авторизованный пользователь |
| GET, POST | `/api/habits/` | Только свои привычки |
| GET, PUT, PATCH, DELETE | `/api/habits/{id}/` | Только владелец |
| GET | `/api/habits/public/` | Все, только чтение |
| GET | `/api/schema/` | Все |
| GET | `/api/docs/` | Все |
| GET | `/api/redoc/` | Все |

Для защищённых запросов передавайте заголовок:

```http
Authorization: Bearer <access_token>
```

Пример создания привычки:

```json
{
  "place": "Дома",
  "time": "19:00:00",
  "action": "Прочитать 10 страниц книги",
  "is_pleasant": false,
  "related_habit": null,
  "periodicity": 1,
  "reward": "Чашка чая",
  "execution_time": 120,
  "is_public": false
}
```

## Валидация

- нельзя передавать одновременно `related_habit` и `reward`;
- `execution_time` не больше 120 секунд;
- `periodicity` должна быть от 1 до 7 дней;
- связанная привычка должна быть приятной и принадлежать текущему пользователю;
- приятная привычка не может иметь вознаграждение или связанную привычку;
- привычка не может быть связана сама с собой.

## Проверки качества

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=users --cov=habits --cov=telegram_bot --cov-report=term-missing --cov-fail-under=80
.\.venv\Scripts\ruff.exe check config users habits telegram_bot tests manage.py
.\.venv\Scripts\ruff.exe format --check config users habits telegram_bot tests manage.py
```
