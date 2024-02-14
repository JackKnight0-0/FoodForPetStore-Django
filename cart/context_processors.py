import uuid

from .models import Cart


def cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        try:
            cart = Cart.objects.get(session_id=request.session.get('nunusercart', None), user=None)
        except Cart.DoesNotExist:
            session_id = str(uuid.uuid4())
            request.session['nunusercart'] = session_id
            cart = Cart.objects.create(session_id=session_id)
    return {'cart': cart}
