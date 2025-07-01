from django.shortcuts import render
from api.models import ProductFilial, Debtor, MCart, MOrder, ProductPriceType, Sum
from django.http.response import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

@require_GET
def abot_index(request, chat_id):
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
            'som':product_dict.get(i['id'], {}).get('sum',10),
            'measurement_type__name':i['measurement_type__name'],
        }
        data.append(dt)

    m_order = MOrder.objects.filter(debtor=customer, status=1).last()
    cart_data = []
    if m_order:
        m_cart = MCart.objects.filter(m_order=m_order)
        for cr in m_cart:
            cr_dt = {
                'product_id': cr.product.id,
                'quantity': cr.quantity,
                'price': cr.price,
                'name': cr.product.name,
                'measurement': cr.product.measurement_type.name if cr.product.measurement_type else ''
            }
            cart_data.append(cr_dt)

    context = {
        'product': data,
        'customer': customer,
        'is_telegram': is_telegram,
        'chat_id': chat_id,
        'initial_cart_data': json.dumps(cart_data)  
    }
    return render(request, 'abot/index.html', context)

@csrf_exempt
def add_to_cart(request, chat_id):
    try:
        data = json.loads(request.body)
        customer = Debtor.objects.filter(tg_id=chat_id).first()
        if not customer:
            return JsonResponse({'error': 'Customer not found'}, status=404)
        
        m_order = MOrder.objects.filter(debtor=customer, status=1).last()
        if not m_order:
            m_order = MOrder.objects.create(debtor=customer, status=1)
        
        product = ProductFilial.objects.get(id=data['product_id'])
        cart_item, created = MCart.objects.get_or_create(
            m_order=m_order,
            debtor=customer,
            product=product,
            defaults={
                'quantity': data['quantity'],
                'price': data['price']
            }
        )
        if not created:
            cart_item.quantity = data['quantity']
            cart_item.price = data['price']
            cart_item.save()
        m_order.is_confirmed = False
        m_order.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def remove_from_cart(request, chat_id):
    try:
        data = json.loads(request.body)
        customer = Debtor.objects.filter(tg_id=chat_id).first()
        if not customer:
            return JsonResponse({'error': 'Customer not found'}, status=404)
        m_order = MOrder.objects.filter(debtor=customer, status=1).last()
        if not m_order:
            return JsonResponse({'ok': True})  
        cart_item = MCart.objects.filter(
            m_order=m_order,
            debtor=customer,
            product_id=data['product_id'],
        ).last()
        cart_item.delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def mobile_done_cart(request, chat_id):
    try:
        customer = Debtor.objects.filter(tg_id=chat_id).first()
        if not customer:
            return JsonResponse({'error': 'Customer not found'}, status=404)
        m_order = MOrder.objects.filter(debtor=customer, status=1).last()
        if not m_order:
            return JsonResponse({'error': 'No active order found'}, status=404)
        m_order.status = 2 
        m_order.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



def debtor_orders(request, chat_id):
    order = MOrder.objects.filter(debtor__tg_id=chat_id)
    context = {
        'order': order,
        'chat_id': chat_id,
    }
    return render(request, 'abot/debtor_orders.html', context)


def debtor_order_detail(request, order_id ,chat_id):
    order = MOrder.objects.get(id=order_id)
    cart = MCart.objects.filter(m_order=order)
    context = {
        'order': order,
        'chat_id': chat_id,
        'cart':cart,
    }
    return render(request, 'abot/debtor_order_detail.html', context)
