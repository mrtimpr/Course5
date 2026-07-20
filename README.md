# Habit Tracker API

Backend SPA-приложения для управления полезными и приятными привычками.
Пользователи регистрируются и авторизуются по JWT, управляют собственными
привычками, просматривают публичные привычки и получают Telegram-напоминания,
которые запускаются по расписанию через Celery Beat.

Проект контейнеризирован и разворачивается одной командой через Docker Compose.
GitHub Actions выполняет линтинг, тестирование, проверку миграций и OpenAPI,
запускает все Docker-сервисы, выполняет HTTP smoke-тест и после успешных
проверок автоматически деплоит ветку `develop` на удалённый сервер.

## Состав проекта

Основные технологии:

- Python 3.12;
- Django и Django REST Framework;
- PostgreSQL;
- Redis;
- Celery Worker и Celery Beat;
- Gunicorn;
- Nginx;
- Docker и Docker Compose;
- GitHub Actions;
- Pytest, coverage и Ruff.

## Docker-сервисы

В `docker-compose.yml` описаны все необходимые сервисы.

| Сервис | Назначение |
|---|---|
| `db` | PostgreSQL, основная база данных |
| `redis` | брокер сообщений Celery |
| `migrate` | одноразовое применение миграций и сбор статики |
| `web` | Django API, запущенный через Gunicorn |
| `celery_worker` | выполнение фоновых задач |
| `celery_beat` | постановка задач Telegram-напоминаний по расписанию |
| `nginx` | reverse proxy, единая точка входа, раздача static/media |

PostgreSQL, Redis, Django и Nginx имеют healthcheck. Сервисы Django и Celery
запускаются только после успешного завершения миграций и готовности зависимостей.

## Требования для локального запуска

Установите:

- Git;
- Docker Desktop для Windows/macOS или Docker Engine для Linux;
- Docker Compose Plugin.

Проверьте установку:

```bash
docker --version
docker compose version
```

Команды чувствительны к регистру только в документации: фактически используйте
`docker`, как в примерах ниже.

## Локальный запуск

### 1. Клонирование проекта

```bash
git clone <адрес-репозитория>
cd <папка-проекта>
```

### 2. Создание файла окружения

Linux/macOS:

```bash
cp .env.template .env
```

Windows PowerShell:

```powershell
Copy-Item .env.template .env
```

Измените минимум следующие значения:

```env
SECRET_KEY=длинный-случайный-секретный-ключ
POSTGRES_PASSWORD=надёжный-пароль
DATABASE_URL=postgresql://habit_user:надёжный-пароль@db:5432/habit_tracker
TELEGRAM_BOT_TOKEN=токен-от-BotFather
```

Значения `POSTGRES_PASSWORD` и пароль внутри `DATABASE_URL` должны совпадать.

### 3. Запуск всех сервисов одной командой

```bash
docker compose up -d --build
```

Команда собирает образ приложения и запускает PostgreSQL, Redis, миграции,
Django, Celery Worker, Celery Beat и Nginx.

Проверьте состояние:

```bash
docker compose ps --all
```

Сервис `migrate` должен иметь состояние `Exited (0)`. Это нормальное состояние:
он выполняет миграции и `collectstatic`, после чего завершается.

### 4. Адреса приложения

При стандартном `HTTP_PORT=80`:

- API и Nginx: `http://localhost/`;
- healthcheck: `http://localhost/health/`;
- Django Admin: `http://localhost/admin/`;
- Swagger: `http://localhost/api/docs/`;
- ReDoc: `http://localhost/api/redoc/`;
- OpenAPI schema: `http://localhost/api/schema/`.

### 5. Создание администратора

```bash
docker compose exec web python manage.py createsuperuser
```

В проекте используется авторизация по email.

## Управление контейнерами

Просмотр логов всех сервисов:

```bash
docker compose logs -f
```

Логи конкретного сервиса:

```bash
docker compose logs -f web
docker compose logs -f celery_worker
docker compose logs -f celery_beat
docker compose logs -f nginx
```

Перезапуск:

```bash
docker compose restart
```

Остановка:

```bash
docker compose down
```

Остановка с удалением данных PostgreSQL и Redis:

```bash
docker compose down -v
```

Последняя команда удаляет локальную базу данных. Используйте её только тогда,
когда данные больше не нужны.

## Миграции

Миграции должны создаваться разработчиком и храниться в Git. Контейнеры не
выполняют `makemigrations` во время production-запуска.

После изменения моделей:

```bash
docker compose run --rm web python manage.py makemigrations
```

Добавьте созданные файлы миграций в коммит. При следующем запуске одноразовый
сервис `migrate` автоматически выполнит:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

Проверка отсутствия незакоммиченных изменений моделей:

```bash
docker compose run --rm web python manage.py makemigrations --check --dry-run
```

## Проверка качества локально

Линтинг и форматирование:

```bash
docker compose run --rm web ruff check config users habits telegram_bot tests manage.py
docker compose run --rm web ruff format --check config users habits telegram_bot tests manage.py
```

Тесты и покрытие:

```bash
docker compose run --rm web pytest \
  --cov=users \
  --cov=habits \
  --cov=telegram_bot \
  --cov-report=term-missing \
  --cov-fail-under=80
```

Django checks:

```bash
docker compose run --rm web python manage.py check
```

Проверка Compose:

```bash
docker compose config --quiet
```

## Telegram и Celery

1. Создайте Telegram-бота через BotFather.
2. Запишите токен в `TELEGRAM_BOT_TOKEN` файла `.env`.
3. Пользователь должен открыть чат с ботом и отправить `/start`.
4. Сохраните `telegram_chat_id` пользователя через API.
5. Создайте привычку с требуемым временем и периодичностью.

`celery_beat` раз в минуту запускает проверку привычек. `celery_worker`
отправляет уведомления через Telegram Bot API. Запись `HabitNotification`
защищает от повторной отправки одного уведомления в один день.

## CI/CD

Workflow расположен в `.github/workflows/ci-cd.yml`.

### Когда запускается pipeline

- при создании или обновлении Pull Request в `develop`;
- при push/merge в `develop`.

### Этап `quality`

1. Запускает PostgreSQL и Redis как сервисы GitHub Actions.
2. Устанавливает Python 3.12 и зависимости.
3. Запускает `ruff check` и `ruff format --check`.
4. Проверяет, что миграции созданы и закоммичены.
5. Применяет миграции к тестовой PostgreSQL.
6. Запускает Django system checks.
7. Валидирует OpenAPI-схему.
8. Запускает Pytest с минимальным покрытием 80%.

### Этап `docker-compose`

1. Проверяет синтаксис `docker-compose.yml`.
2. Собирает Docker-образ приложения.
3. Запускает все сервисы через Docker Compose.
4. Ожидает успешный ответ `/health/`.
5. Проверяет состояние сервисов и Django.
6. При ошибке выводит логи контейнеров.

### Этап `deploy`

Этап выполняется только после успешного merge/push в `develop`:

1. Подключается к серверу по SSH.
2. Передаёт только актуальные файлы проекта через `rsync`.
3. Создаёт на сервере защищённый `.env` из GitHub Secret `PROD_ENV`.
4. Выполняет `docker compose up -d --build --remove-orphans`.
5. Ожидает успешный production healthcheck.
6. Запускает `python manage.py check` внутри контейнера.
7. При ошибке выводит состояние и логи сервисов, после чего pipeline завершается
   с ошибкой.

## Подготовка удалённого сервера

Ниже приведён пример для Ubuntu.

### 1. Создание пользователя для деплоя

```bash
sudo adduser deploy
sudo usermod -aG sudo deploy
```

### 2. Установка Docker и Compose Plugin

```bash
sudo apt update
sudo apt install -y ca-certificates curl git rsync
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

sudo usermod -aG docker deploy
```

Выйдите из SSH-сессии и подключитесь снова, чтобы членство в группе `docker`
применилось.

Проверка:

```bash
docker --version
docker compose version
docker run --rm hello-world
```

### 3. Подготовка каталога проекта

```bash
sudo mkdir -p /opt/habit_tracker_backend
sudo chown -R deploy:deploy /opt/habit_tracker_backend
```

### 4. Настройка firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw enable
```

При использовании HTTPS дополнительно откройте порт `443/tcp`.

## Настройка SSH для GitHub Actions

Создайте отдельный ключ без парольной фразы:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f github_actions_deploy
```

Скопируйте публичный ключ на сервер:

```bash
ssh-copy-id -i github_actions_deploy.pub deploy@SERVER_IP
```

Проверьте вход:

```bash
ssh -i github_actions_deploy deploy@SERVER_IP
```

Содержимое приватного файла `github_actions_deploy` сохраните в GitHub Secret
`DEPLOY_SSH_KEY`. Приватный ключ нельзя добавлять в репозиторий.

Для `DEPLOY_KNOWN_HOSTS` выполните локально:

```bash
ssh-keyscan -H -p 22 SERVER_IP
```

Скопируйте полученную строку целиком в соответствующий GitHub Secret.

## GitHub Secrets

Откройте:

```text
Repository → Settings → Secrets and variables → Actions
```

Добавьте:

| Secret | Пример | Назначение |
|---|---|---|
| `DEPLOY_HOST` | `203.0.113.10` | IP или домен сервера |
| `DEPLOY_USER` | `deploy` | SSH-пользователь |
| `DEPLOY_PORT` | `22` | SSH-порт |
| `DEPLOY_PATH` | `/opt/habit_tracker_backend` | каталог проекта |
| `DEPLOY_SSH_KEY` | многострочный приватный ключ | SSH-доступ к серверу |
| `DEPLOY_KNOWN_HOSTS` | результат `ssh-keyscan` | проверка SSH host key |
| `PROD_ENV` | полное содержимое production `.env` | production-настройки |

Пример `PROD_ENV`:

```env
SECRET_KEY=production-long-random-secret
DEBUG=False
ALLOWED_HOSTS=api.example.com,203.0.113.10,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://api.example.com,http://203.0.113.10
TIME_ZONE=Europe/Helsinki
LOG_LEVEL=INFO
DATABASE_CONN_MAX_AGE=60

SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0

POSTGRES_DB=habit_tracker
POSTGRES_USER=habit_user
POSTGRES_PASSWORD=replace-with-strong-password
DATABASE_URL=postgresql://habit_user:replace-with-strong-password@db:5432/habit_tracker

CORS_ALLOWED_ORIGINS=https://frontend.example.com
CORS_ALLOW_CREDENTIALS=True

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

TELEGRAM_BOT_TOKEN=replace-with-real-token
TELEGRAM_API_URL=https://api.telegram.org
TELEGRAM_REQUEST_TIMEOUT=10

JWT_ACCESS_MINUTES=60
JWT_REFRESH_DAYS=7
HTTP_PORT=80
IMAGE_TAG=latest
```

Если HTTPS уже настроен на внешнем reverse proxy или load balancer, установите:

```env
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

Не включайте эти значения до рабочего HTTPS, иначе приложение начнёт
перенаправлять запросы на недоступный HTTPS-адрес.

## Ветки и Pull Request

Рекомендуемый порядок выполнения задания:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/docker-ci-cd
```

Добавьте только файлы, относящиеся к контейнеризации и CI/CD:

```text
.github/workflows/ci-cd.yml
.dockerignore
.env.template
.gitattributes
.gitignore
Dockerfile
docker-compose.yml
nginx/default.conf
scripts/startup.sh
scripts/deploy.sh
config/settings.py
config/urls.py
requirements.txt
pyproject.toml
README.md
users/migrations/
habits/migrations/
```

После проверки:

```bash
git add <перечень-нужных-файлов>
git commit -m "Add Docker Compose and CI/CD deployment"
git push -u origin feature/docker-ci-cd
```

Создайте Pull Request:

```text
feature/docker-ci-cd → develop
```

Автодеплой выполняется после успешного прохождения pipeline и merge в
`develop`.

## Диагностика

### Контейнер `migrate` завершился с ошибкой

```bash
docker compose logs migrate
```

Проверьте `DATABASE_URL`, пароль PostgreSQL и наличие миграций в репозитории.

### Django или Celery не подключается к PostgreSQL

В Docker-окружении хост базы должен быть `db`, а не `localhost`:

```env
DATABASE_URL=postgresql://habit_user:password@db:5432/habit_tracker
```

### Celery не подключается к Redis

В Docker-окружении хост Redis должен быть `redis`:

```env
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Nginx возвращает 502

```bash
docker compose ps --all
docker compose logs web
docker compose logs nginx
```

Проверьте, что `web` имеет состояние `healthy`.

### Production deploy не запускается

Проверьте:

- workflow был запущен событием `push` в `develop`;
- все GitHub Secrets заполнены;
- SSH-пользователь может выполнять `docker` без `sudo`;
- каталог `DEPLOY_PATH` принадлежит SSH-пользователю;
- на сервере установлены `docker compose`, `rsync` и `curl`;
- порты SSH и HTTP открыты в firewall.
