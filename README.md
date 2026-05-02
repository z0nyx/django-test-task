## Сервер:

ip самого сервера: http://193.58.121.10:8000/

Прочие url для теста:
```text
http://193.58.121.10:8000/item/1
http://193.58.121.10:8000/buy/1
http://193.58.121.10:8000/order/1
http://193.58.121.10:8000/order/1/buy
http://193.58.121.10:8000/payment-intent/item/1
```

### Данные для входа в админ панель:
- username: admin
- пароль: admin123

## Локальный запуск

```bash
cp .env.example .env
```

Заполнить .env окружение:

```env
POSTGRES_DB=app
POSTGRES_USER=app
POSTGRES_PASSWORD=

DJANGO_SECRET_KEY=
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1

DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SECURE_HSTS_SECONDS=0
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=False
DJANGO_SECURE_HSTS_PRELOAD=False
DJANGO_SESSION_COOKIE_SECURE=False
DJANGO_CSRF_COOKIE_SECURE=False

DJANGO_SUPERUSER_USERNAME=
DJANGO_SUPERUSER_EMAIL=
DJANGO_SUPERUSER_PASSWORD=
DJANGO_SUPERUSER_RESET_PASSWORD=False

STRIPE_PUBLIC_KEY=pk_test_
STRIPE_SECRET_KEY=sk_test_
```

```env
STRIPE_PUBLIC_KEY=pk
STRIPE_SECRET_KEY=sk
```


Установка и запуск:

Linux: 
```bash
python3 -m venv .venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py ensure_admin
python manage.py runserver
```

Windows:
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py ensure_admin
python manage.py runserver
```

Адрес:

```text
http://127.0.0.1:8000/
```

## Docker запуск

```bash
cp .env.example .env
docker compose up --build
```

После запуска:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/admin/
```

## Тестовые URL

После `seed_demo` доступны:

```text
http://127.0.0.1:8000/item/1
http://127.0.0.1:8000/buy/1
http://127.0.0.1:8000/order/1
http://127.0.0.1:8000/order/1/buy
http://127.0.0.1:8000/payment-intent/item/1
```

## Админка

`ensure_admin` создаёт админа. Настройка тут в .env окружении:

```env
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin-password
```

Затем выполнить:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```
