from django.urls import path

import payments.views as views

urlpatterns = [
    path('checkout/', views.CheckOutSessionView.as_view(), name='checkout'),
    path('success/', views.SuccessCheckoutView.as_view(), name='success_checkout'),
    path('cancel/', views.CancelCheckoutView.as_view(), name='cancel_checkout'),
    path('orders/', views.MyOrderList.as_view(), name='order_list'),
    path('user/orders/', views.AllUserOrdersList.as_view(), name='order_user_list'),
    path('change-order-status/<slug:slug>/', views.ChangeOrderStatus.as_view(), name='order_change_status'),
    path('order/<slug:slug>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('webhook/', views.StripeWebHookView.as_view(), name='stripe_webhook'),
]
