from allauth.account.views import LoginView, SignupView, PasswordChangeView, PasswordResetView, \
    PasswordResetFromKeyView

import accounts.forms as forms

from cart.models import Cart, CartItem


class CustomLoginView(LoginView):
    form_class = forms.CustomLoginForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        cart = self.get_cart()
        response = super().form_valid(form=form)
        user = self.request.user
        if user.cart and cart is not None:
            user_cart, user_cart_created = Cart.objects.get_or_create(user=user)
            items = cart.items.all()
            if items:
                for item in items:
                    user_item, user_item_created = CartItem.objects.get_or_create(item=item.item, cart=user_cart)
                    if user_item_created:
                        user_item.quantity = item.quantity
                    else:
                        user_item.quantity += item.quantity
                    user_item.save()
            user_cart.update_total_amount()
            cart.delete()
        elif cart is not None:
            cart.session_id = None
            cart.user = user
            cart.save()
        return response

    def get_cart(self):
        if self.request.session.get('nunusercart', False):
            cart = Cart.objects.filter(session_id=self.request.session.get('nunusercart')).first()
            del self.request.session['nunusercart']
            return cart
        return None


class CustomSignupView(SignupView):
    form_class = forms.CustomSignUpForm
    template_name = 'accounts/signup.html'

    def get_cart(self):
        if self.request.session.get('nunusercart', False):
            cart = Cart.objects.filter(session_id=self.request.session.get('nunusercart')).first()
            del self.request.session['nunusercart']
            return cart
        return None

    def form_valid(self, form):
        cart = self.get_cart()
        response = super().form_valid(form=form)

        print(cart)
        if cart is not None:
            cart.user = self.request.user
            cart.session_id = None
            cart.save()
        return response


class CustomChangePasswordView(PasswordChangeView):
    form_class = forms.CustomChangePasswordForm
    template_name = 'accounts/change_password.html'


class CustomResetPasswordView(PasswordResetView):
    form_class = forms.CustomResetPasswordForm
    template_name = 'accounts/password_reset.html'


class CustomResetPasswordFromKeyView(PasswordResetFromKeyView):
    form_class = forms.CustomResetPasswordFromKeyForm
    template_name = 'accounts/password_reset_from_key.html'
