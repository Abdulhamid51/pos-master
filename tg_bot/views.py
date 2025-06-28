from django.shortcuts import render
from api.models import ProductFilial, Debtor, MCart, MOrder, ProductPriceType, Sum
from django.http.response import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt


def telegram_webapp(request, tg_id):
    customer = Debtor.objects.filter(tg_id=tg_id).first()
    products = ProductFilial.objects.select_related("measurement_type")[:10]

    return render(request, "abot/index.html", {
        "customer": customer,
        "product": products,
        "order_id": tg_id 
    })

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