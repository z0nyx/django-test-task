from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

import stripe
from django.conf import settings
from django.urls import reverse

from payments.exceptions import OrderCurrencyError, PaymentConfigurationError, StripeGatewayError
from payments.models import Item, Order


MINOR_UNIT_MULTIPLIER = Decimal("100")
MINOR_UNIT_QUANTIZER = Decimal("1")
ZERO_DECIMAL_CURRENCIES = frozenset(
    {
        "bif",
        "clp",
        "djf",
        "gnf",
        "jpy",
        "kmf",
        "krw",
        "mga",
        "pyg",
        "rwf",
        "ugx",
        "vnd",
        "vuv",
        "xaf",
        "xof",
        "xpf",
    }
)


@dataclass(frozen=True)
class StripeKeys:
    public_key: str
    secret_key: str


def stripe_keys_for_currency(currency: str) -> StripeKeys:
    normalized_currency = currency.lower()
    configured_keys = settings.STRIPE_CURRENCY_KEYS.get(normalized_currency)
    if not configured_keys:
        raise PaymentConfigurationError(f"Currency {normalized_currency} is not supported")

    public_key = configured_keys.get("public", "")
    secret_key = configured_keys.get("secret", "")

    if not public_key or not secret_key:
        raise PaymentConfigurationError(f"Stripe keys for {normalized_currency.upper()} are not configured")

    return StripeKeys(public_key=public_key, secret_key=secret_key)


def stripe_public_key_for_currency(currency: str) -> str:
    return stripe_keys_for_currency(currency).public_key


def amount_to_minor_units(amount: Decimal, currency: str) -> int:
    if currency.lower() in ZERO_DECIMAL_CURRENCIES:
        normalized_amount = amount.quantize(MINOR_UNIT_QUANTIZER, rounding=ROUND_HALF_UP)
    else:
        normalized_amount = (amount * MINOR_UNIT_MULTIPLIER).quantize(MINOR_UNIT_QUANTIZER, rounding=ROUND_HALF_UP)
    return int(normalized_amount)


def build_item_line(item: Item, tax_rate_ids: list[str] | None = None) -> dict:
    line_item = {
        "price_data": {
            "currency": item.currency,
            "unit_amount": amount_to_minor_units(item.price, item.currency),
            "product_data": {
                "name": item.name,
                "description": item.description,
            },
        },
        "quantity": 1,
    }

    if tax_rate_ids:
        line_item["tax_rates"] = tax_rate_ids

    return line_item


def checkout_success_url(request) -> str:
    return request.build_absolute_uri(reverse("payment_success")) + "?session_id={CHECKOUT_SESSION_ID}"


def create_item_checkout_session(item: Item, request):
    stripe_keys = stripe_keys_for_currency(item.currency)
    cancel_url = request.build_absolute_uri(item.get_absolute_url())

    try:
        return stripe.checkout.Session.create(
            api_key=stripe_keys.secret_key,
            mode="payment",
            payment_method_types=["card"],
            line_items=[build_item_line(item)],
            success_url=checkout_success_url(request),
            cancel_url=cancel_url,
            metadata={"item_id": str(item.pk)},
        )
    except stripe.error.StripeError as error:
        raise StripeGatewayError(str(error)) from error


def order_items(order: Order) -> list[Item]:
    items = list(order.items.all())
    if not items:
        raise PaymentConfigurationError("Order has no items")

    currencies = {item.currency for item in items}
    if len(currencies) != 1:
        raise OrderCurrencyError("Order items must use one currency")

    return items


def create_discount_coupon(order: Order, api_key: str) -> str | None:
    if not order.discount_id:
        return None

    try:
        coupon = stripe.Coupon.create(
            api_key=api_key,
            duration="once",
            name=order.discount.name,
            percent_off=float(order.discount.percent_off),
            metadata={"discount_id": str(order.discount_id), "order_id": str(order.pk)},
        )
        return coupon.id
    except stripe.error.StripeError as error:
        raise StripeGatewayError(str(error)) from error


def create_tax_rate(order: Order, api_key: str) -> str | None:
    if not order.tax_id:
        return None

    try:
        tax_rate = stripe.TaxRate.create(
            api_key=api_key,
            display_name=order.tax.name,
            inclusive=order.tax.inclusive,
            percentage=float(order.tax.percentage),
            metadata={"tax_id": str(order.tax_id), "order_id": str(order.pk)},
        )
        return tax_rate.id
    except stripe.error.StripeError as error:
        raise StripeGatewayError(str(error)) from error


def create_order_checkout_session(order: Order, request):
    items = order_items(order)
    currency = items[0].currency
    stripe_keys = stripe_keys_for_currency(currency)
    coupon_id = create_discount_coupon(order, stripe_keys.secret_key)
    tax_rate_id = create_tax_rate(order, stripe_keys.secret_key)
    tax_rate_ids = [tax_rate_id] if tax_rate_id else []
    discounts = [{"coupon": coupon_id}] if coupon_id else []
    line_items = [build_item_line(item, tax_rate_ids) for item in items]
    cancel_url = request.build_absolute_uri(order.get_absolute_url())

    try:
        return stripe.checkout.Session.create(
            api_key=stripe_keys.secret_key,
            mode="payment",
            payment_method_types=["card"],
            line_items=line_items,
            discounts=discounts,
            success_url=checkout_success_url(request),
            cancel_url=cancel_url,
            metadata={"order_id": str(order.pk)},
        )
    except stripe.error.StripeError as error:
        raise StripeGatewayError(str(error)) from error


def create_item_payment_intent(item: Item):
    stripe_keys = stripe_keys_for_currency(item.currency)

    try:
        return stripe.PaymentIntent.create(
            api_key=stripe_keys.secret_key,
            amount=amount_to_minor_units(item.price, item.currency),
            currency=item.currency,
            payment_method_types=["card"],
            metadata={"item_id": str(item.pk)},
        )
    except stripe.error.StripeError as error:
        raise StripeGatewayError(str(error)) from error
