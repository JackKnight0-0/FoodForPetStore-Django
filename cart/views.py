import uuid

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views import generic

from .models import Cart, CartItem
from .utils import CartMixin

from store.utils import SortMixin
from store.models import BaseItem


class AddItemToCartView(generic.View):
    """
    The view for adding item to cart
    """

    def get_item(self):
        """
        Getting item from url and return BaseItem if found.
        """
        return get_object_or_404(BaseItem, pk=self.kwargs.get('item_pk'))

    def get_success_url(self):
        """
        Return user to the previous page.
        """
        return redirect(self.request.META.get('HTTP_REFERER'))

    def add_to_cart(self):
        """
        Method is checking if a user is authenticated or anonymous and checking the condition to add item.
        """
        item = self.get_item()
        if self.request.user.is_authenticated:
            """
            If user is authenticated getting or creating cart and saving or increase quantity of item to cart.
            """
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            item, created = CartItem.objects.get_or_create(cart=cart, item=item)
            item.quantity += 1
            item.save()
            cart.update_total_amount()
        else:
            """If user is anonymous, trying get the cart by session uuid and if not exists creating for session 
            uuid and saving uuid to cart"""
            try:
                cart = Cart.objects.get(session_id=self.request.session['nunusercart'])
                item, created = CartItem.objects.get_or_create(cart=cart, item=item)
                item.quantity += 1
                item.save()
                cart.update_total_amount()
            except:
                self.request.session['nunusercart'] = str(uuid.uuid4())
                cart = Cart.objects.create(session_id=self.request.session['nunusercart'])
                item, created = CartItem.objects.get_or_create(cart=cart, item=item)
                item.quantity += 1
                item.save()
                cart.update_total_amount()

    def post(self, request, *args, **kwargs):
        self.add_to_cart()
        return self.get_success_url()


class MyListCart(CartMixin, SortMixin, generic.ListView):
    """
    View is display the items in cart and return list of BaseItems.

    The view is extended with CartMixin.
    """
    template_name = 'cart/my_cart_items.html'
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super(MyListCart, self).get_context_data(**kwargs)
        context['cart'] = self.get_my_cart()
        return self.update_context(context=context)

    def check_items_out_of_stock(self, items, cart):
        """
        If a user adds to cart a lot of items,
        and it's bigger than item quantity than the method is stabilizing the amount of item.
        """
        for item in items:
            if item.item.quantity < item.quantity:
                item.quantity = item.item.quantity
                item.save()
        cart.update_total_amount()

    def get_queryset(self):
        cart = self.get_my_cart()
        self.check_items_out_of_stock(cart.items.all(), cart)
        return self.sort_items(cart.items, ordering='item__price')


class DecreaseIncreaseCartItem(CartMixin, generic.View):
    """
    This view is decreasing or increasing the amount of item
    """

    def get_success_url(self):
        return redirect(self.request.META.get('HTTP_REFERER'))

    def decrease_increase_item(self):
        """
        Getting the operation from post and checking the board of item if it's not zero, and the amount of cart item is
        not bigger than quantity item
        """
        cart_item = self.get_cart_item()
        cart = self.get_my_cart()
        op = self.request.POST.get('op')
        if cart_item.quantity > 1 and op == 'decrease':
            cart_item.quantity -= 1
            cart_item.save()
            cart.update_total_amount()
        elif op == 'increase' and cart_item.item.quantity >= cart_item.quantity + 1:
            cart_item.quantity += 1
            cart_item.save()
            cart.update_total_amount()

    def post(self, request, *args, **kwargs):
        self.decrease_increase_item()
        return self.get_success_url()


class DeleteCartItem(CartMixin, generic.View):
    """
    This view is deleting cart item by item pk and return to the previous page.
    """

    def delete_cart_item(self):
        cart = self.get_cart_or_404()
        cart_item = self.get_cart_item()
        cart_item.delete()
        cart.update_total_amount()

    def get_success_url(self):
        return redirect(self.request.META.get('HTTP_REFERER'))

    def post(self, request, *args, **kwargs):
        self.delete_cart_item()
        return self.get_success_url()
