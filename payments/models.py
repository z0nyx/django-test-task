from decimal import Decimal, ROUND_HALF_UP

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


MONEY_QUANTIZER = Decimal("0.01")
PRICE_MINIMUM = Decimal("0.01")
PERCENT_MINIMUM = Decimal("0.01")
PERCENT_MAXIMUM = Decimal("100.00")
PERCENT_DIVISOR = Decimal("100.00")
ZERO_MONEY = Decimal("0.00")


def rounded_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANTIZER, rounding=ROUND_HALF_UP)


class Currency(models.TextChoices):
    USD = "usd", "USD"
    EUR = "eur", "EUR"


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(PRICE_MINIMUM)],
    )
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("item_detail", kwargs={"item_id": self.pk})


class Discount(models.Model):
    name = models.CharField(max_length=255)
    percent_off = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(PERCENT_MINIMUM), MaxValueValidator(PERCENT_MAXIMUM)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} {self.percent_off}%"


class Tax(models.Model):
    name = models.CharField(max_length=255)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(PERCENT_MINIMUM), MaxValueValidator(PERCENT_MAXIMUM)],
    )
    inclusive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} {self.percentage}%"


class OrderStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PAID = "paid", "Paid"
    CANCELED = "canceled", "Canceled"


class Order(models.Model):
    items = models.ManyToManyField(Item, related_name="orders")
    discount = models.ForeignKey(Discount, related_name="orders", on_delete=models.SET_NULL, null=True, blank=True)
    tax = models.ForeignKey(Tax, related_name="orders", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=16, choices=OrderStatus.choices, default=OrderStatus.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order {self.pk or 'new'}"

    def get_absolute_url(self) -> str:
        return reverse("order_detail", kwargs={"order_id": self.pk})

    def item_list(self) -> list[Item]:
        if not self.pk:
            return []
        return list(self.items.all())

    def currency(self) -> str:
        currencies = {item.currency for item in self.item_list()}
        if not currencies:
            return ""
        if len(currencies) == 1:
            return next(iter(currencies))
        return "mixed"

    def items_subtotal(self) -> Decimal:
        subtotal = sum((item.price for item in self.item_list()), ZERO_MONEY)
        return rounded_money(subtotal)

    def discount_amount(self) -> Decimal:
        if not self.discount_id:
            return ZERO_MONEY
        discount_value = self.items_subtotal() * self.discount.percent_off / PERCENT_DIVISOR
        return rounded_money(discount_value)

    def taxable_amount(self) -> Decimal:
        return rounded_money(max(self.items_subtotal() - self.discount_amount(), ZERO_MONEY))

    def tax_amount(self) -> Decimal:
        if not self.tax_id or self.tax.inclusive:
            return ZERO_MONEY
        tax_value = self.taxable_amount() * self.tax.percentage / PERCENT_DIVISOR
        return rounded_money(tax_value)

    def total_price(self) -> Decimal:
        return rounded_money(self.taxable_amount() + self.tax_amount())
