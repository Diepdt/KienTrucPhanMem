# micro/cart_service/cart/views.py
"""
Views cho Cart Service - Quản lý giỏ hàng
Giao tiếp với Book Service và Customer Service qua HTTP API
"""
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Cart, CartItem

# URLs của các Service khác
BOOK_SERVICE_URL = "http://127.0.0.1:8002/api/books/"
CUSTOMER_SERVICE_URL = "http://127.0.0.1:8001/api/customers/"


@csrf_exempt
def add_to_cart_api(request):
    """
    API: Thêm sách vào giỏ hàng.
    Logic:
    1. Nhận customer_id và book_id từ request body
    2. Gọi API đến Book Service để kiểm tra tồn kho và lấy giá
    3. Lưu vào database của Cart Service
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer_id = data.get('customer_id')
            book_id = data.get('book_id')
            quantity = data.get('quantity', 1)

            # Validate input
            if not customer_id or not book_id:
                return JsonResponse({
                    'success': False, 
                    'error': 'customer_id and book_id are required'
                }, status=400)

            # 1. Gọi API sang Book Service để lấy thông tin sách
            try:
                book_response = requests.get(f"{BOOK_SERVICE_URL}{book_id}/", timeout=5)
                if book_response.status_code != 200:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Book not found in Book Service'
                    }, status=404)
                
                book_data = book_response.json()
                
                # Kiểm tra tồn kho
                if book_data['stock'] < quantity:
                    return JsonResponse({
                        'success': False, 
                        'error': f"Out of stock. Only {book_data['stock']} available."
                    }, status=400)

            except requests.exceptions.RequestException as e:
                return JsonResponse({
                    'success': False, 
                    'error': f'Cannot connect to Book Service: {str(e)}'
                }, status=503)

            # 2. Xử lý Logic Giỏ hàng - Lưu vào Database của Cart Service
            cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
            
            # Kiểm tra xem sách đã có trong giỏ chưa
            existing_item = CartItem.objects.filter(cart=cart, book_id=book_id).first()
            if existing_item:
                existing_item.quantity += quantity
                existing_item.save()
                message = f"Updated quantity to {existing_item.quantity}"
            else:
                CartItem.objects.create(
                    cart=cart,
                    book_id=book_id,
                    quantity=quantity,
                    price=book_data['price'],  # Lưu snapshot giá tại thời điểm thêm vào giỏ
                    book_title=book_data.get('title', '')  # Lưu tên sách để hiển thị
                )
                message = 'Added to cart'
            
            return JsonResponse({
                'success': True, 
                'message': message,
                'book_title': book_data.get('title', '')
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'error': 'Invalid JSON'
            }, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


def get_cart_api(request, customer_id):
    """
    API: Lấy thông tin giỏ hàng của khách hàng.
    """
    try:
        cart = Cart.objects.get(customer_id=customer_id)
        items_data = []
        total = 0
        
        for item in cart.items.all():
            item_total = float(item.price) * item.quantity
            total += item_total
            items_data.append({
                'id': item.id,
                'book_id': item.book_id,
                'book_title': item.book_title,
                'quantity': item.quantity,
                'price': float(item.price),
                'item_total': item_total
            })
            
        return JsonResponse({
            'success': True,
            'customer_id': customer_id,
            'items': items_data,
            'total_price': total,
            'item_count': len(items_data)
        })
        
    except Cart.DoesNotExist:
        return JsonResponse({
            'success': True,
            'customer_id': customer_id,
            'items': [],
            'total_price': 0,
            'item_count': 0
        })


@csrf_exempt
def update_cart_item_api(request):
    """
    API: Cập nhật số lượng item trong giỏ hàng.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            action = data.get('action')  # 'increase' hoặc 'decrease'
            
            cart_item = CartItem.objects.get(id=item_id)
            
            if action == 'increase':
                # Kiểm tra tồn kho trước khi tăng
                try:
                    book_response = requests.get(
                        f"{BOOK_SERVICE_URL}{cart_item.book_id}/", 
                        timeout=5
                    )
                    if book_response.status_code == 200:
                        book_data = book_response.json()
                        if book_data['stock'] > cart_item.quantity:
                            cart_item.quantity += 1
                            cart_item.save()
                        else:
                            return JsonResponse({
                                'success': False, 
                                'error': 'Out of stock'
                            })
                except requests.exceptions.RequestException:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Cannot verify stock'
                    })
                    
            elif action == 'decrease':
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
                    return JsonResponse({
                        'success': True, 
                        'message': 'Item removed'
                    })
            
            return JsonResponse({
                'success': True, 
                'new_quantity': cart_item.quantity
            })
            
        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Cart item not found'
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'error': 'Invalid JSON'
            }, status=400)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def remove_from_cart_api(request):
    """
    API: Xóa item khỏi giỏ hàng.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            
            cart_item = CartItem.objects.get(id=item_id)
            cart_item.delete()
            
            return JsonResponse({
                'success': True, 
                'message': 'Item removed from cart'
            })
            
        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Cart item not found'
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'error': 'Invalid JSON'
            }, status=400)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)