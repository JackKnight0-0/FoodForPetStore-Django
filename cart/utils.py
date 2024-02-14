import uuid

from django.shortcuts import get_object_or_404

from store.models import BaseItem

from .models import Cart, CartItem


class CartMixin(object):
    def get_my_cart(self):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            return cart
        else:
            try:
                cart = Cart.objects.get(session_id=self.request.session.get('nunusercart'), user=None)
                return cart
            except:
                self.request.session['nunusercart'] = str(uuid.uuid4())
                cart = Cart.objects.create(session_id=self.request.session.get('nunusercart'))
                return cart

    def get_cart_or_404(self):
        if self.request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=self.request.user)
        else:
            cart = get_object_or_404(Cart, session_id=self.request.session.get('nunusercart'))
        return cart

    def get_item(self, item_pk):
        return get_object_or_404(BaseItem, pk=item_pk)

    def get_cart_item(self):
        cart = self.get_cart_or_404()
        item = self.get_item(item_pk=self.kwargs.get('item_pk'))
        cart_item = get_object_or_404(CartItem, cart=cart, item=item)
        return cart_item
