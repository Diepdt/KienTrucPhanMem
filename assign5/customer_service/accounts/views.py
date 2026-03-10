from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Customer
import json

@csrf_exempt
def register_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            customer = Customer.objects.create(
                name=data['name'],
                email=data['email'],
                password=data['password']
            )
            return JsonResponse({'success': True, 'id': customer.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def login_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            customer = Customer.objects.get(email=data['email'], password=data['password'])
            return JsonResponse({
                'success': True, 
                'customer': {'id': customer.id, 'name': customer.name, 'email': customer.email}
            })
        except Customer.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'})
    return JsonResponse({'success': False}, status=405)

def get_customer_api(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        return JsonResponse({
            'id': customer.id, 'name': customer.name, 'email': customer.email
        })
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)