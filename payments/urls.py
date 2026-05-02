from django.urls import path

from payments import views


urlpatterns = [
    path("", views.index, name="index"),
    path("item/<int:item_id>", views.item_detail, name="item_detail"),
    path("buy/<int:item_id>", views.buy_item, name="buy_item"),
    path("order/<int:order_id>", views.order_detail, name="order_detail"),
    path("order/<int:order_id>/buy", views.buy_order, name="buy_order"),
    path("payment-intent/item/<int:item_id>", views.payment_intent_item, name="payment_intent_item"),
    path("payment-intent/item/<int:item_id>/create", views.create_payment_intent_for_item, name="create_payment_intent_for_item"),
    path("success/", views.payment_success, name="payment_success"),
    path("cancel/", views.payment_cancel, name="payment_cancel"),
]
