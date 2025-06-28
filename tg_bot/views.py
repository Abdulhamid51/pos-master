from django.shortcuts import render
from api.models import ProductFilial, Debtor, MCart, MOrder, ProductPriceType, Sum, Shop, Cart
from django.http.response import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone


def abot_index(request, order_id):
    order = MOrder.objects.get(id=order_id)
    customer = Debtor.objects.filter(id=order.debtor.id).first()
    product = ProductFilial.objects.order_by('-id').values('id', 'name', 'quantity', 'image', 'som', 'measurement_type__name')
    price_type =  customer.price_type 
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
            'product' :data,
            'customer':customer,
            'order_id':order_id,
    }
    return render(request, 'abot/index.html', context)


@csrf_exempt
def mobile_done_cart(request, order_id):
    data = json.loads(request.body)
    order = MOrder.objects.get(id=order_id)
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
    return JsonResponse({'ok':True})




def cart_webapp(request, order_id):
    m_order, created = MOrder.objects.get_or_create(id=order_id)
    
    products = [
        {
            'id': 1,
            'name': 'Giggles baby taglik (N°3)',
            'description': '68 Sht',
            'price': 91000
        },
        {
            'id': 2,
            'name': 'Giggles baby taglik (N°2)',
            'description': '76 Sht',
            'price': 83993
        },
        {
            'id': 3,
            'name': 'Baby One baby taglik (N°2)',
            'description': '38 Sht',
            'price': 41002
        }
    ]
    
    return render(request, 'cart.html', {
        'order_id': order_id,
        'products': products
    })

@csrf_exempt
def webapp_callback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            products = data.get('products')
            
            # Process the order
            m_order = MOrder.objects.get(id=order_id)
            shop_order = Shop.objects.create(
                debtor=m_order.debtor,
                total_price=sum(p['price'] * p['quantity'] for p in products),
                date=timezone.now()
            )
            
            for product in products:
                Cart.objects.create(
                    shop=shop_order,
                    product=ProductFilial.objects.get(id=product['id']),
                    quantity=product['quantity'],
                    price=product['price'],
                    total_price=product['price'] * product['quantity']
                )
            
            return JsonResponse({'status': 'success', 'order_id': shop_order.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})