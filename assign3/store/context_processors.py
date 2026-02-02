"""
Context processors for the store app.
"""
from store.models import Cart


def cart_context(request):
    """
    Add cart information to all template contexts.
    """
    cart_count = 0
    
    customer_id = request.session.get('customer_id')
    
    if customer_id:
        try:
            from store.models import Customer
            customer = Customer.objects.get(id=customer_id)
            cart = Cart.objects.filter(customer=customer).first()
            if cart:
                cart_count = cart.get_total_items()
        except:
            pass
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, customer__isnull=True)
                cart_count = cart.get_total_items()
            except:
                pass
    
    return {
        'cart_count': cart_count,
    }
