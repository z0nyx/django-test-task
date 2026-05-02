# Django Stripe Payments

Реализация тестового задания: Django backend с Stripe Checkout Session, HTML-страницами оплаты, Django Admin и бонусными задачами.

## Этапы разработки

- `day1`: обязательный минимум с `Item`, `/item/<id>`, `/buy/<id>` и Stripe Checkout.
- `day2`: добавлены Docker, env-конфигурация, Django Admin и security-настройки.
- `day3`: добавлены бонусные модели, валюты, Order Checkout и Payment Intent.
- Корень проекта: финальная версия четвёртого дня.

## Что реализовано

- Модель `Item` с полями `name`, `description`, `price`, `currency`.
- `GET /item/<id>`: HTML-страница товара с кнопкой `Buy`.
- `GET /buy/<id>`: создание `stripe.checkout.Session` и возврат `session.id`.
- Модель `Order`, объединяющая несколько `Item`.
- `GET /order/<id>` и `GET /order/<id>/buy`: оплата заказа через Stripe Checkout.
- Модели `Discount` и `Tax`, которые применяются при создании Stripe Checkout Session.
- Разные Stripe keypair для `usd` и `eur`.
- Дополнительный Payment Intent flow: `/payment-intent/item/<id>`.
- Django Admin для всех моделей.
- Docker и `docker-compose.yml`.
- Конфигурация через `.env`.
- CSP, security headers, CSRF для POST Payment Intent endpoint.

## Локальный запуск

```bash
cp .env.example .env
```

Заполните Stripe ключи в `.env`. Можно использовать общий keypair:

```env
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
```

Или разные ключи по валютам:

```env
STRIPE_PUBLIC_KEY_USD=pk_test_xxx
STRIPE_SECRET_KEY_USD=sk_test_xxx
STRIPE_PUBLIC_KEY_EUR=pk_test_xxx
STRIPE_SECRET_KEY_EUR=sk_test_xxx
```

Установка и запуск:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py ensure_admin
python manage.py runserver
```

Приложение будет доступно по адресу:

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

Команда `ensure_admin` создаёт администратора из переменных:

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
