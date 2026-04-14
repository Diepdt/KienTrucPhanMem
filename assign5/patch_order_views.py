import re

with open(r'c:\django\assign5\order-service\order\views.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update clear_cart function
old_clear_cart = '''def clear_cart(customer_id):
    try:
        http_requests.post(
            f"{django_settings.CART_SERVICE_URL}/api/carts/{customer_id}/clear/",
            timeout=5)
    except Exception as e:
        logger.error(f"clear_cart error: {e}")'''
        
new_clear_cart = '''def clear_cart(customer_id):
    try:
        http_requests.post(
            f"{django_settings.CART_SERVICE_URL}/api/carts/{customer_id}/clear/",
            timeout=5)
    except Exception as e:
        logger.error(f"clear_cart error: {e}")'''

code = code.replace(old_clear_cart, new_clear_cart)

with open(r'c:\django\assign5\order-service\order\views.py', 'w', encoding='utf-8') as f:
    f.write(code)
