from django.db import models
from django.contrib.auth import get_user_model

from store.models import BaseItem


class Cart(models.Model):
    """
    Represent of a cart model for user, can be used for authenticated user and for anonymous user.

    This model is having a function for getting items from cart and update the total price.
    """

    user = models.OneToOneField(to=get_user_model(), related_name='cart', on_delete=models.CASCADE, null=True,
                                blank=True)
    session_id = models.UUIDField(null=True, blank=True)
    total_amount = models.DecimalField(editable=False, default=0, decimal_places=2, max_digits=10)

    def item_count(self):
        """
        The function is returning total count of items in the cart.
        """
        return self.items.count()

    def update_total_amount(self):
        """
        Updating the total price of items for cart and save it.
        """
        items = self.items.all()
        self.total_amount = 0
        for item in items:
            self.total_amount += (item.quantity * item.item.price)
        self.save()

    def __str__(self):
        return str(self.pk)


class CartItem(models.Model):
    """
    Represent a cart item model, saving the item and quantity of item.
    """
    cart = models.ForeignKey(to=Cart, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(to=BaseItem, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField(default=0, blank=True)

    def __str__(self):
        return self.item.name

    class Meta:
        ordering = ['item']
