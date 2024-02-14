import json
import uuid

from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, reverse, get_object_or_404
from django.template.loader import render_to_string
from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Count
from django.core.mail import EmailMessage

import stripe

from .models import OrderDetail, OrderItem
from .forms import ChangeOrderStatusForm

from cart.models import Cart
from store.models import BaseItem

stripe.api_key = settings.STRIPE_PRIVATE_KEY


class CheckOutSessionView(generic.View):
    """
    This view is for checkout, using the Strip API to make checkout for user.
    """
    def get_cart(self):
        """
        Getting the cart from user or anonymous user and checking if items in this cart existing.
        """
        if self.request.user.is_authenticated:
            cart = self.request.user.cart
        else:
            cart = Cart.objects.annotate(total=Count(F('items'))).filter(
                session_id=self.request.session.get('nunusercart', None), total__gt=0).first()
        if cart is None or not cart.items.all():
            raise Http404()
        return cart

    def check_items_out_of_stock(self, items):
        """
        Checking if items not out of stock, because another user could already buy them.
        """
        for item in items:
            if item.item.quantity < item.quantity:
                raise Http404

    def get_user_pk(self):
        """
        Method is return the user pk or nunuser for metadata in payments.
        """
        if self.request.user.is_authenticated:
            return self.request.user.pk
        return 'nunuser'

    def post(self, request, *args, **kwargs):
        """
        Using the strip API
        """
        user_cart = self.get_cart()
        items = user_cart.items.all()
        self.check_items_out_of_stock(items)

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data':
                        {'currency': 'usd',
                         'unit_amount': int((item.item.price) * 100),
                         'product_data': {
                             'name': item.item.name,
                             'description': item.item.description,
                             'images': [
                                 f"http://127.0.0.1:8000/{item.item.images.first().image_of_item.path}"
                             ],
                         }},
                    'quantity': item.quantity
                } for item in items
            ],
            metadata={
                'product_id': str(uuid.uuid4()),
                'items': json.dumps([{'item_pk': item.item.pk, 'item_quantity': item.quantity} for item in items]),
                'user_pk': str(self.get_user_pk()),
                'cart_pk': str(self.get_cart())
            },
            mode='payment',
            success_url='http://127.0.0.1:8000/payment/success/',
            cancel_url='http://127.0.0.1:8000/payment/cancel/',
            shipping_address_collection={'allowed_countries': ['US', 'DE']},

        )
        return redirect(checkout_session.url)


class SuccessCheckoutView(generic.TemplateView):
    """
    Showing success payment operation template.
    """
    template_name = 'payments/success.html'


class CancelCheckoutView(generic.TemplateView):
    """
    Showing cancel payment operation template.
    """
    template_name = 'payments/cancel.html'


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebHookView(generic.View):
    """
    This view for stripe webhook, to process the payment after it was successful done.
    """

    def send_email(self, order, email):
        """
        Sending email to user after purchase was done.

        Order and email as parameter needed.
        """
        domain = get_current_site(request=self.request)
        subject = 'Thank you for shopping with us! #' + str(order.pk)
        message = render_to_string(template_name='payments/mail/order_created.html',
                                   context={'order': order, 'domain': domain})
        email_message = EmailMessage(subject=subject, body=message, to=[email, ])
        email_message.send()

    def get_cart(self, cart_pk):
        cart = Cart.objects.get(pk=cart_pk)
        return cart

    def clean_cart(self, cart):
        cart.items.all().delete()
        cart.update_total_amount()

    def create_order(self, product_id, email, shipping_details, shipping_address, cart, items, user_pk):
        """
        Creating order from data in session object
        """
        order = OrderDetail.objects.create(slug=product_id, name=shipping_details['name'], email=email,
                                           city=shipping_address['city'], country=shipping_address['country'],
                                           address=shipping_address['line1'],
                                           postal_code=shipping_address['postal_code'],
                                           total_amount=cart.total_amount)

        for payment_item in items:
            item = BaseItem.objects.get(pk=payment_item['item_pk'])
            OrderItem.objects.create(item=item, order=order, quantity=payment_item['item_quantity'])
            item.quantity -= payment_item['item_quantity']
            item.save()

        if user_pk != 'nunuser':
            order.user_id = user_pk
            order.save()

        return order

    def post(self, request, *args, **kwargs):
        """
        Using strip API to process the webhook.
        """
        payload = request.body
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            """Checking signature"""
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            email = session['customer_details']['email']
            metadata = session['metadata']
            user_pk = metadata['user_pk']
            shipping_details = session['shipping_details']
            shipping_address = shipping_details['address']
            product_id = metadata['product_id']
            items = json.loads(metadata['items'])

            cart = self.get_cart(metadata['cart_pk'])

            order = self.create_order(product_id=product_id, email=email, shipping_details=shipping_details,
                                      shipping_address=shipping_address, cart=cart, items=items, user_pk=user_pk)

            self.clean_cart(cart)

            self.send_email(order=order, email=order.email)

        return HttpResponse(status=200)


class OrderDetailView(generic.DetailView):
    """
    This view is showing the order from slug.
    """
    template_name = 'payments/order_detail.html'
    model = OrderDetail
    slug_url_kwarg = 'slug'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context['form'] = ChangeOrderStatusForm(instance=self.get_object())
        return context


class MyOrderList(LoginRequiredMixin, generic.ListView):
    """
    If user is authenticated showing his order list.
    """
    template_name = 'payments/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return OrderDetail.objects.filter(user=self.request.user).order_by('-created_at')


class AllUserOrdersList(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    """
    Showing all orders for admin only.
    """
    template_name = 'payments/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return OrderDetail.objects.all()

    def test_func(self):
        return self.request.user.is_staff


class ChangeOrderStatus(LoginRequiredMixin, UserPassesTestMixin, generic.FormView):
    """
    This view is for updating order status, and send email with update message.
    """
    form_class = ChangeOrderStatusForm

    def send_message(self, order, email):
        """
        Send email to user if the order status was updated.
        """
        domain = get_current_site(request=self.request)
        body = render_to_string(template_name='payments/mail/message.html',
                                context={'domain': domain, 'order': order})
        subject = 'Your order #' + str(order.pk) + ' was updated'

        send_message = EmailMessage(subject=subject, body=body, to=[email, ])
        send_message.send()

    def get_object(self):
        return get_object_or_404(OrderDetail, slug=self.kwargs.get('slug'))

    def get_success_url(self):
        return redirect(reverse('order_detail', kwargs={'slug': self.kwargs.get('slug')}))

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        form = ChangeOrderStatusForm(self.request.POST, instance=order)

        if form.is_valid():
            form.save()
            self.send_message(order=order, email=order.email)

            return self.get_success_url()

    def test_func(self):
        return self.request.user.is_staff
