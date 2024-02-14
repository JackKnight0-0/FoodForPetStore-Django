from django.urls import path

import cart.views as views

urlpatterns = [
    path('add/<int:item_pk>/', views.AddItemToCartView.as_view(), name='add_item_to_cart'),
    path('my/cart/', views.MyListCart.as_view(), name='my_cart'),
    path('remove-add/item/<int:item_pk>/', views.DecreaseIncreaseCartItem.as_view(), name='remove_add_cart_item'),
    path('delete/item/<int:item_pk>/', views.DeleteCartItem.as_view(), name='delete_item_from_cart')
]
