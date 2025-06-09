from django.shortcuts import render
from api.models import ProductFilial, Debtor, MCart, MOrder
from django.http.response import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

def abot_index(request, order_id):
    order = MOrder.objects.get(id=order_id)
    customer = Debtor.objects.filter(id=order.debtor.id).first()
    context = {
            'product' :ProductFilial.objects.order_by('-id').values('id', 'name', 'quantity', 'image', 'som', 'measurement_type__name'),
            'customer':customer,
            'order_id':order_id,
    }
    return render(request, 'abot/index.html', context)


@csrf_exempt
def mobile_done_cart(request, oder_id):
    data = json.dumps(request.body)
    order = MOrder.objects.get(id=oder_id)
    back = []

    for item in data:
        cart_item = MCart.objects.create(
            debtor=order.debtor,
            product_id=item['product_id'],  
            price=item['price'],
            quantity=item['quantity'],
            status=2
        )
        back.append(cart_item)
    order.products.set(back)
    order.save()
    return JsonResponse({'ok':True})