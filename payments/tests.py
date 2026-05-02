from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from payments.models import Discount, Item, Order, Tax
from payments.stripe_gateway import amount_to_minor_units


STRIPE_TEST_KEYS = {
    "usd": {
        "public": "pk_test_usd",
        "secret": "sk_test_usd",
    },
    "eur": {
        "public": "pk_test_eur",
        "secret": "sk_test_eur",
    },
}


class PaymentViewTests(TestCase):
    def setUp(self):
        self.item = Item.objects.create(
            name="Test Item",
            description="Test description",
            price=Decimal("12.34"),
            currency="usd",
        )

    @override_settings(STRIPE_CURRENCY_KEYS=STRIPE_TEST_KEYS)
    def test_item_page_renders(self):
        response = self.client.get(reverse("item_detail", kwargs={"item_id": self.item.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Item")
        self.assertContains(response, "pk_test_usd")

    @override_settings(STRIPE_CURRENCY_KEYS=STRIPE_TEST_KEYS)
    def test_buy_item_returns_session_id(self):
        with patch("payments.stripe_gateway.stripe.checkout.Session.create") as session_create:
            session_create.return_value = SimpleNamespace(id="cs_test_123")
            response = self.client.get(reverse("buy_item", kwargs={"item_id": self.item.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": "cs_test_123"})
        session_create.assert_called_once()

    @override_settings(STRIPE_CURRENCY_KEYS=STRIPE_TEST_KEYS)
    def test_order_checkout_includes_discount_and_tax(self):
        second_item = Item.objects.create(
            name="Second Item",
            description="Second description",
            price=Decimal("5.00"),
            currency="usd",
        )
        discount = Discount.objects.create(name="Discount", percent_off=Decimal("10.00"))
        tax = Tax.objects.create(name="Tax", percentage=Decimal("5.00"), inclusive=False)
        order = Order.objects.create(discount=discount, tax=tax)
        order.items.set([self.item, second_item])

        with patch("payments.stripe_gateway.stripe.Coupon.create") as coupon_create, patch("payments.stripe_gateway.stripe.TaxRate.create") as tax_create, patch("payments.stripe_gateway.stripe.checkout.Session.create") as session_create:
            coupon_create.return_value = SimpleNamespace(id="coupon_test")
            tax_create.return_value = SimpleNamespace(id="txr_test")
            session_create.return_value = SimpleNamespace(id="cs_order_test")
            response = self.client.get(reverse("buy_order", kwargs={"order_id": order.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": "cs_order_test"})
        session_arguments = session_create.call_args.kwargs
        self.assertEqual(session_arguments["discounts"], [{"coupon": "coupon_test"}])
        self.assertEqual(session_arguments["line_items"][0]["tax_rates"], ["txr_test"])

    @override_settings(STRIPE_CURRENCY_KEYS=STRIPE_TEST_KEYS)
    def test_mixed_currency_order_is_rejected(self):
        eur_item = Item.objects.create(
            name="EUR Item",
            description="EUR description",
            price=Decimal("9.00"),
            currency="eur",
        )
        order = Order.objects.create()
        order.items.set([self.item, eur_item])

        response = self.client.get(reverse("buy_order", kwargs={"order_id": order.pk}))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Order items must use one currency"})

    @override_settings(STRIPE_CURRENCY_KEYS=STRIPE_TEST_KEYS)
    def test_payment_intent_returns_client_secret(self):
        with patch("payments.stripe_gateway.stripe.PaymentIntent.create") as payment_intent_create:
            payment_intent_create.return_value = SimpleNamespace(client_secret="pi_secret_test")
            response = self.client.post(reverse("create_payment_intent_for_item", kwargs={"item_id": self.item.pk}), data={})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"clientSecret": "pi_secret_test"})


class AmountConversionTests(TestCase):
    def test_decimal_currency_amount_uses_minor_units(self):
        self.assertEqual(amount_to_minor_units(Decimal("12.34"), "usd"), 1234)

    def test_zero_decimal_currency_amount_uses_integer_units(self):
        self.assertEqual(amount_to_minor_units(Decimal("1200"), "jpy"), 1200)
