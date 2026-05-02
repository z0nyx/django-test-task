from decimal import Decimal

from django.core.management.base import BaseCommand

from payments.models import Discount, Item, Order, Tax


class Command(BaseCommand):
    help = "Creates demo payment data"

    def handle(self, *args, **options):
        usd_item = Item.objects.update_or_create(
            name="Demo USD Item",
            defaults={
                "description": "A demo item for Stripe Checkout in USD",
                "price": Decimal("19.99"),
                "currency": "usd",
            },
        )[0]
        Item.objects.update_or_create(
            name="Demo EUR Item",
            defaults={
                "description": "A demo item for Stripe Checkout in EUR",
                "price": Decimal("24.50"),
                "currency": "eur",
            },
        )
        second_usd_item = Item.objects.update_or_create(
            name="Demo USD Add-on",
            defaults={
                "description": "An additional item for order checkout",
                "price": Decimal("7.25"),
                "currency": "usd",
            },
        )[0]
        discount = Discount.objects.update_or_create(
            name="Demo Discount",
            defaults={"percent_off": Decimal("10.00")},
        )[0]
        tax = Tax.objects.update_or_create(
            name="Demo Tax",
            defaults={"percentage": Decimal("6.50"), "inclusive": False},
        )[0]
        order = Order.objects.update_or_create(
            pk=1,
            defaults={"discount": discount, "tax": tax, "status": "draft"},
        )[0]
        order.items.set([usd_item, second_usd_item])
        self.stdout.write("Demo data is ready")
