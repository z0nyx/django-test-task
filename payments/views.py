import logging
from http import HTTPStatus

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST

from payments.exceptions import OrderCurrencyError, PaymentConfigurationError, StripeGatewayError
from payments.models import Item, Order
from payments.stripe_gateway import (
    create_item_checkout_session,
    create_item_payment_intent,
    create_order_checkout_session,
    stripe_public_key_for_currency,
)


logger = logging.getLogger(__name__)


def json_error(message: str, status: HTTPStatus) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


def payment_configuration_error_response(error: Exception) -> JsonResponse:
    logger.warning("Payment configuration error: %s", error)
    return json_error(str(error), HTTPStatus.BAD_REQUEST)


def stripe_gateway_error_response(error: Exception) -> JsonResponse:
    logger.warning("Stripe gateway error: %s", error)
    return json_error("Unable to create Stripe payment", HTTPStatus.BAD_GATEWAY)


@require_GET
def index(request):
    items = Item.objects.all()
    orders = Order.objects.prefetch_related("items").select_related("discount", "tax")
    return render(request, "payments/index.html", {"items": items, "orders": orders})


@require_GET
def item_detail(request, item_id: int):
    item = get_object_or_404(Item, pk=item_id)

    try:
        stripe_public_key = stripe_public_key_for_currency(item.currency)
    except PaymentConfigurationError as error:
        logger.warning("Payment configuration error: %s", error)
        stripe_public_key = ""

    return render(request, "payments/item_detail.html", {"item": item, "stripe_public_key": stripe_public_key})


@require_GET
def buy_item(request, item_id: int):
    item = get_object_or_404(Item, pk=item_id)

    try:
        session = create_item_checkout_session(item, request)
    except PaymentConfigurationError as error:
        return payment_configuration_error_response(error)
    except StripeGatewayError as error:
        return stripe_gateway_error_response(error)

    return JsonResponse({"id": session.id})


@require_GET
def order_detail(request, order_id: int):
    order = get_object_or_404(Order.objects.prefetch_related("items").select_related("discount", "tax"), pk=order_id)
    currency = order.currency()

    try:
        stripe_public_key = stripe_public_key_for_currency(currency) if currency and currency != "mixed" else ""
    except PaymentConfigurationError as error:
        logger.warning("Payment configuration error: %s", error)
        stripe_public_key = ""

    return render(request, "payments/order_detail.html", {"order": order, "stripe_public_key": stripe_public_key})


@require_GET
def buy_order(request, order_id: int):
    order = get_object_or_404(Order.objects.prefetch_related("items").select_related("discount", "tax"), pk=order_id)

    try:
        session = create_order_checkout_session(order, request)
    except (PaymentConfigurationError, OrderCurrencyError) as error:
        return payment_configuration_error_response(error)
    except StripeGatewayError as error:
        return stripe_gateway_error_response(error)

    return JsonResponse({"id": session.id})


@require_GET
def payment_intent_item(request, item_id: int):
    item = get_object_or_404(Item, pk=item_id)

    try:
        stripe_public_key = stripe_public_key_for_currency(item.currency)
    except PaymentConfigurationError as error:
        logger.warning("Payment configuration error: %s", error)
        stripe_public_key = ""

    return render(request, "payments/payment_intent_item.html", {"item": item, "stripe_public_key": stripe_public_key})


@require_POST
def create_payment_intent_for_item(request, item_id: int):
    item = get_object_or_404(Item, pk=item_id)

    try:
        payment_intent = create_item_payment_intent(item)
    except PaymentConfigurationError as error:
        return payment_configuration_error_response(error)
    except StripeGatewayError as error:
        return stripe_gateway_error_response(error)

    return JsonResponse({"clientSecret": payment_intent.client_secret})


@require_GET
def payment_success(request):
    return render(request, "payments/success.html")


@require_GET
def payment_cancel(request):
    return render(request, "payments/cancel.html")
