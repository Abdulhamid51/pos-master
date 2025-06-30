from django.shortcuts import render
from api.models import ProductFilial, Debtor, MCart, MOrder, ProductPriceType, Sum
from django.http.response import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

@require_GET
def abot_index(request, chat_id):
    # Check if this is a Telegram Web App request
    is_telegram = request.headers.get('User-Agent', '').lower().find('telegram') != -1
    
    customer = Debtor.objects.filter(tg_id=chat_id).first()
    if not customer:
        return JsonResponse({'error': 'Customer not found'}, status=404)
    
    product = ProductFilial.objects.order_by('-id').values('id', 'name', 'quantity', 'image', 'som', 'measurement_type__name')
    price_type = customer.price_type
    product_price = ProductPriceType.objects.filter(type=price_type, valyuta__is_som=True).values('product_id').annotate(sum=Sum('price'))
    product_dict = {item['product_id']:item for item in product_price}
    
    data = []
    for i in product:
        dt = {
            'id':i['id'],
            'name':i['name'],
            'quantity':i['quantity'],
            'image':i['image'],
            'som':product_dict.get(i['id'], {}).get('sum',0),
            'measurement_type__name':i['measurement_type__name'],
        }
        data.append(dt)
    
    context = {
        'product': data,
        'customer': customer,
        'is_telegram': is_telegram,
        'chat_id': chat_id,
        'web_app_mode': True,
    }
    return render(request, 'abot/index.html', context)

@csrf_exempt
def mobile_done_cart(request, chat_id):
    try:
        data = json.loads(request.body)
        order = MOrder.objects.create(debtor_id=chat_id)
        back = []

        for item in data:
            cart_item = MCart.objects.create(
                debtor=order.debtor,
                product_id=item['product_id'],  
                price=item['price'],
                quantity=item['quantity'],
                status=2
            )
            product = ProductFilial.objects.get(id=item['product_id'])
            product.quantity -= item['quantity']
            product.save()
            back.append(cart_item)
        
        order.products.set(back)
        order.save()
        return JsonResponse({'ok': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)