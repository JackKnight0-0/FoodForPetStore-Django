from django.db import models
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from store.models import BaseItem


class OrderDetail(models.Model):
    """
    Represent of an order detail model,
    to store the information about order and manipulate with order status and ship number through staff user.
    """

    class StatusChoice(models.TextChoices):
        """
        The status of order, by default, is PENDING.
        """
        PENDING = ('PENDING', 'Pending')
        SENT = ('SENT', 'Sent')
        DELIVERED = ('DELIVERED', 'Delivered')
        CANCELED = ("CANCELED", 'Canceled')
        __empty__ = 'Status'

    user = models.ForeignKey(to=get_user_model(), related_name='orders', on_delete=models.CASCADE, null=True,
                             blank=True)
    ship_number = models.CharField(max_length=500, blank=True, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(editable=False, db_index=True)
    email = models.EmailField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    postal_code = models.PositiveIntegerField()
    status = models.CharField(choices=StatusChoice, default=StatusChoice.PENDING)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=7, decimal_places=2)

    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-created_at', ]


class OrderItem(models.Model):
    """
    This model is representing the order item for store information about how many items user got.
    """
    order = models.ForeignKey('OrderDetail', related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(BaseItem, related_name='orders', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
