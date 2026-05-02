from django.contrib import admin

from payments.models import Discount, Item, Order, Tax


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "price", "currency", "created_at"]
    list_filter = ["currency", "created_at"]
    search_fields = ["name", "description"]


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "percent_off", "created_at"]
    search_fields = ["name"]


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "percentage", "inclusive", "created_at"]
    list_filter = ["inclusive", "created_at"]
    search_fields = ["name"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "currency", "items_subtotal", "discount_amount", "tax_amount", "total_price", "created_at"]
    list_filter = ["status", "created_at"]
    filter_horizontal = ["items"]
    autocomplete_fields = ["discount", "tax"]
