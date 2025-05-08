import requests
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import action, api_view
from .models import MobilUser, Telegramid, MyOwnToken,MOrder, MCart, ProductFilial, Banner, Debtor, UserProfile, Region, Teritory, \
ProductCategory, PayHistory, Filial, PayChecker
from rest_framework import viewsets
from .authentication import MyOwnTokenAuthentication
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import MCartSerializer, MOrderSerializer, ProductFilialSerializer, BannerSerializer, DebtorSerializer, \
PayHistorySerializer, PayCheckerSerializer,DesktopKassaSerializer
from datetime import date
from decimal import Decimal

@api_view(['GET'])
def region_apiview(request):
    region = Region.objects.filter(is_active=True).order_by('number')
    data = []
    for i in region:
        dt = {
            'id': i.id,
            'name': i.name
        }
        data.append(dt)
    return Response(data)

@api_view(['GET'])
def teritory_apiview(request):
    region = request.GET.get('region')
    teritory = Teritory.objects.filter(region_id=region, is_active=True).order_by('number')
    data = []
    for i in teritory:
        dt = {
            'id': i.id,
            'name': i.name
        }
        data.append(dt)
    return Response(data)

class NewDebtorViewSet(viewsets.ModelViewSet):
    queryset = Debtor.objects.all()
    serializer_class = DebtorSerializer
    authentication_classes = (MyOwnTokenAuthentication, TokenAuthentication)
    permission_classes = ()

    def get_queryset(self):
        queryset = self.queryset.filter(agent=self.request.user)
        return queryset
    
    def create(self, request):
        request.data._mutable = True
        request.data['agent'] = request.user.id
        request.data._mutable = False
        return super().create(request)
    
    
    # @action(methods=['post'], detail=True)
    # def upload_image(self, request):
    #     image = request.FILES.get('img')

class DesktopDebtorViewSet(viewsets.ModelViewSet):
    queryset = Debtor.objects.all()
    serializer_class = DebtorSerializer

#update debtor
@api_view(['POST'])
def update_debtors(request):
    try:
        id = request.data['id']
        fio = request.data['fio']
        phone = request.data['phone']
        phone2 = request.data['phone2']
        #nasiyachi
        debtor = Debtor.objects.get(id = id)
        debtor.fio = fio
        debtor.phone1 = phone
        debtor.phone2 = phone2
        debtor.save()
        data = {
            'status':True,
            'message': f'{id} nasiyachi {fio} ga va {phone} yangilandi'
        }
    except Exception as e:
        data = {
        'status':False,
        'message': f'{e} '
    }
    return Response(data)

#Get and return debtor id for desktop
@api_view(['GET'])
def get_debtor_by_name(request):
    try:
        fio = request.GET.get("fio")
        phone = request.GET.get("phone")
        
        #nasiyachi
        debtor, created = Debtor.objects.get_or_create(fio=fio, phone1=phone)
        id = debtor.id
        data = {
            'status':True,
            'message': id,
        }
        return JsonResponse(data, status=200)
    except Exception as e:
        data = {
        'status':False,
        'message': f'{e} '
    }
        return JsonResponse(data, status=404)

@api_view(['POST'])
def login(request):
    phone = request.data['phone']
    password = request.data['password']

    try:
        cl = MobilUser.objects.get(phone=phone)
        if password == cl.password:
            status = 200
            try:
                myT = MyOwnToken.objects.get(user_id=cl.id)
            except MyOwnToken.DoesNotExist:
                myT = MyOwnToken.objects.create(user_id=cl.id)

            data = {
                'status': int(status),
                'user': cl.id,
                'token': myT.key,
                "username": cl.username,
            }
        else:
            status = 403
            massage = "Telefon raqam yoki parol xato!"
            data = {
                'status': int(status),
                'massage': massage,
            }
    except MobilUser.DoesNotExist:
        status=404
        massage = "Bunday foydalanuvchi mavjud emas!"
        data = {
            'status': status,
            'massage': massage,
        }

    return Response(data)


@api_view(['POST'])
def register(request):
    phone = request.data['phone']
    password = request.data['password']
    username = request.data['username']
    cl = MobilUser.objects.filter(phone=phone).count()
    if cl > 0:
        status = 203
        massage = "Bunday foydalanuvchi mavjud!"
        token = None
        client_id = None
    else:
        cc = MobilUser.objects.create(phone=phone, password=password, username=username)
        tt = MyOwnToken.objects.create(user_id=cc.id)
        massage = "Success"
        status = 200,
        token = tt.key
        client_id = cc.id
    data = {
        'status': int(status),
        'massage': massage,
        'token': token,
        'user': client_id,
    }
    return Response(data)


class MCartViewset(viewsets.ModelViewSet):
    queryset = MCart.objects.all()
    serializer_class = MCartSerializer
    authentication_classes = (MyOwnTokenAuthentication, TokenAuthentication)
    permission_classes = ()

    def delete(self, request, id):
        MCart.objects.get(id=id).delete()
        return Response({"deleted":True})
    
    def list(self, request):
        queryset = MCart.objects.filter(user=request.user, applied=False)
        return Response(MCartSerializer(queryset, many=True).data)

    # @action(methods=['post'], detail=False)
    # def cart_delete(self, request, *args, **kwargs):
    #     id = kwargs.get('pk')
    #     Cart.objects.get(id=id).delete()

    #     return response({'success': True})

    @action(methods=['post'], detail=False)
    def post(self, request):
        user = request.user
        product = request.data.get('product')
        quantity = request.data.get('quantity')
        debtor = request.data.get('debtor')
        comment = request.data.get('comment')

        pr = ProductFilial.objects.get(id=product)
        if MCart.objects.filter(user=user, debtor_id=debtor, product=pr, status=1).count() > 0:
            return Response({"message": "Bunday maxsulot savatchada bor!"})
        else:
            if pr.sotish_som > 0:
                total = pr.sotish_som * int(quantity)
                MCart.objects.create(debtor_id=debtor, user=user, product=pr, quantity=quantity, price=pr.sotish_som,
                                     status=1, total=total, comment=comment)
            else:
                total = pr.sotish_dollar * int(quantity)
                MCart.objects.create(debtor_id=debtor, user=user, product=pr, quantity=quantity, price=pr.sotish_dollar,
                                     status=1, total=total, comment=comment)
            return Response({"message": "Muvofaqiyatli qo'shildi"})


    @action(methods=['get'], detail=False)
    def get(self, request):
        user = request.user
        debtor = request.GET.get('debtor')
        cart = MCart.objects.filter(user=user, debtor_id=debtor, status='1', applied=False)
        data = []
        for i in cart:
            if i.product.image:
                dt = {
                    'id': i.id,
                    'product': i.product.name,
                    'product_quantity': i.product.quantity,
                    'quantity': int(i.quantity),
                    'price': i.price,
                    'total': i.total,
                    'applied': i.applied,
                    'status': i.status,
                    'comment': i.comment,
                    'image': i.product.image.url,
                }
            else:
                dt = {
                    'id': i.id,
                    'product': i.product.name,
                    'product_quantity': i.product.quantity,
                    'quantity': int(i.quantity),
                    'price': i.price,
                    'total': i.total,
                    'applied': i.applied,
                    'status': i.status,
                    'comment': i.comment,
                    'image': 'Maxsulot rasmi yoq',
                }
            data.append(dt)
        return Response(data)


    @action(methods=['post'], detail=False)
    def buy(self, request):
        user = request.user
        debtor = request.data.get('debtor')
        cart = MCart.objects.filter(debtor_id=debtor, status='1')
        if cart.count() > 0:
            products = ""
            total = 0
            mo = MOrder.objects.create(user=user, debtor_id=debtor)
            for i in cart:
                i.status = '2'
                i.applied = True
                i.save()

                mo.products.add(i)
                mo.total += i.price * i.quantity
                mo.save()
                total += i.price * i.quantity
                dt = f"Maxsulot: {i.product.name}, Soni: {i.quantity}ta, Narxi: {i.price}\nIzoh: {i.comment}\n"
                products += dt

            text = f'Buyurtma : {mo.id}\n' + '\nAgent: ' + mo.user.username +  '\nMijoz: ' + mo.debtor.fio + '\nMijoz nomeri: ' + str(mo.user.phone) + '\nMaxsulotlar: \n' + str(products) + '\njami: ' + str(total)
            url = 'https://api.telegram.org/bot6007881568:AAHIQFBkTNLwsbE0C5rmt67IH16F6BRjKWQ/sendMessage?chat_id=-1001695536220'
            requests.get(url + '&text=' + text)
            # cat_ids = Telegramid.objects.all()
            # chat = []
            # for id in cat_ids:
            #     chat.append(id.telegram_id)

            # for i in chat:
            #     requests.get(url + str(i) + '&text=' + text)
            data = {
                'status': 200,
                'message': "Muvofaqiyatli sotib olindi!",
                'text': text
            }
            return Response(data)
        else:
            return Response({"message": "Savatchada maxsulot yoq"})

class ProductFilialViewset(viewsets.ModelViewSet):
    queryset = ProductFilial.objects.all()
    serializer_class = ProductFilialSerializer
    authentication_classes = (MyOwnTokenAuthentication, TokenAuthentication)
    permission_classes = ()

    def get_queryset(self):
        category = self.request.GET.get('category')
        queryset = self.queryset
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset

    @action(methods=['get'], detail=False)
    def get(self, request):
        product = ProductFilial.objects.filter().order_by('-id')
        category = request.GET.get('category')
        if category:
            product = product.filter(category_id=category)
        debtor = self.request.GET.get('debtor')
        data = []
        for i in product:
            cart = MCart.objects.filter(debtor_id=debtor, product=i, applied=False, status='1').last()
            if cart:
                cart_data = {
                    "id": cart.id,
                    "count": cart.quantity,
                    "comment": cart.comment
                }
            else:
                cart_data = None
            if i.category:
                category = {
                    "id": i.category.id,
                    "name": i.category.name,
                    "image": i.category.image.url,
                }
            else:
                category = None
            if i.image:
                dt = {
                    'id': i.id,
                    'name': i.name,
                    'preparer': i.preparer,
                    'category': category,
                    'som': int(i.som),
                    'sotish_som': int(i.sotish_som),
                    'dollar': int(i.dollar),
                    'sotish_dollar': int(i.sotish_dollar),
                    'group': i.group.name,
                    'measurement': i.measurement,
                    'min_count': int(i.min_count),
                    'filial': i.filial.name,
                    'quantity': int(i.quantity),
                    'cart': cart_data,
                    'image': i.image.url,
                }
                data.append(dt)
            else:
                dt = {
                    'id': i.id,
                    'name': i.name,
                    'preparer': i.preparer,
                    'category': i.category.__str__(),
                    'som': int(i.som),
                    'sotish_som': int(i.sotish_som),
                    'dollar': int(i.dollar),
                    'sotish_dollar': int(i.sotish_dollar),
                    'group': i.group.name,
                    'measurement': i.measurement,
                    'min_count': int(i.min_count),
                    'filial': i.filial.name,
                    'quantity': int(i.quantity),
                    'cart': cart_data,
                    'image': 'Maxsulot rasmi yoq',
                }
                data.append(dt)
        return Response(data)

    @action(methods=['get'], detail=False)
    def search(self, request):
        pr = request.GET.get('product')
        product = ProductFilial.objects.filter(name__icontains=pr)

        data = []
        for i in product:
            if i.image:
                dt = {
                    'id': i.id,
                    'name': i.name,
                    'preparer': i.preparer,
                    'som': int(i.som),
                    'sotish_som': int(i.sotish_som),
                    'dollar': int(i.dollar),
                    'sotish_dollar': int(i.sotish_dollar),
                    'group': i.group.name,
                    'measurement': i.measurement,
                    'min_count': int(i.min_count),
                    'filial': i.filial.name,
                    'quantity': int(i.quantity),
                    'image': i.image.url,
                    'distributsiya': i.distributsiya
                }
                data.append(dt)
            else:
                dt = {
                    'id': i.id,
                    'name': i.name,
                    'preparer': i.preparer,
                    'som': int(i.som),
                    'sotish_som': int(i.sotish_som),
                    'dollar': int(i.dollar),
                    'sotish_dollar': int(i.sotish_dollar),
                    'group': i.group.name,
                    'measurement': i.measurement,
                    'min_count': int(i.min_count),
                    'filial': i.filial.name,
                    'quantity': int(i.quantity),
                    'image': 'Maxsulot rasmi yoq',
                    'distributsiya': i.distributsiya
                }
                data.append(dt)

        return Response(data)




class BannerViewset(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    authentication_classes = (MyOwnTokenAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)



class MOrderViewset(viewsets.ModelViewSet):
    queryset = MOrder.objects.all()
    serializer_class = MOrderSerializer
    authentication_classes = (MyOwnTokenAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            data = super().create(request, *args, **kwargs)
            order_id=data.data['id']
            instance = MOrder.objects.get(id=order_id)
            products = ""
            total = 0
            for i in instance.products.all():
                cart = MCart.objects.get(id=i.id)
                dt = f"- {cart.product.name} -> {cart.quantity}ta * {cart.price}\n\n"
                products += dt
                total += cart.price * cart.quantity
            text = 'Buyurtma: '+ str(instance.id) + '\nMijoz: ' + instance.user.username + '\nMijoz telefon raqami: ' + str(instance.user.phone) + '\n\nMaxsulotlar: \n\n' + products + '\njami: ' + str(total)
            url = 'https://api.telegram.org/bot6007881568:AAHIQFBkTNLwsbE0C5rmt67IH16F6BRjKWQ/sendMessage?chat_id=-1001695536220'
            requests.get(url + '&text=' + text)
            for i in instance.products.all():
                i.applied = True
                i.save()
            return Response({
                'success': True
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'{e}'
            })

    def list(self, request):
        user = request.user
        queryset = self.queryset.filter(user=user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def get_products(self, request):
        order_id = request.GET['order_id']
        order = MOrder.objects.get(id=order_id)

        pr = order.products.all()
        data = []
        for i in pr:
            if i.product.image:
                dt = {
                    'product': i.product.name,
                    'quantity': int(i.quantity),
                    'image': i.product.image.url,
                    'price': i.price,
                }
            else:
                dt = {
                    'product': i.product.name,
                    'quantity': int(i.quantity),
                    'image': "Maxsulot rasmi yoq",
                    'price': i.price,
                }
            data.append(dt)

        return Response(data)


class PaymentDebtorViewSet(viewsets.ModelViewSet):
    queryset = PayHistory.objects.all()
    serializer_class = PayHistorySerializer
    authentication_classes = (MyOwnTokenAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        debtor_id = request.GET.get('debtor_id')
        if debtor_id:
            queryset = self.queryset.filter(debtor_id=debtor_id)
        else:
            queryset = self.queryset.filter(debtor__agent=request.user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        try:
            debtor = request.data.get('debtor')
            som = request.data.get('som')
            dollar = request.data.get('dollar')
            currency = request.data.get('currency')
            comment = request.data.get('comment')
            payment = PayHistory.objects.create(
                debtor_id=debtor,
                som=float(som),
                dollar=float(dollar),
                filial=Filial.objects.first(),
                currency=float(currency),
                comment=comment
            )
            debtor = payment.debtor
            debtor.som -= float(som)
            debtor.dollar -= float(dollar)
            debtor.save()
            return Response({
                'success': True,
                'data': PayHistorySerializer(payment, many=False).data
            })
        except Exception as error:
            return Response({
                'success': False,
                'error': f'{error}'
            }, status=400)

    @action(methods=['get'], detail=False)
    def requests(self, request):
        chpays = PayChecker.objects.filter(status=False)
        serializer = PayCheckerSerializer(chpays, many=True)
        return Response(serializer.data)
    
    @action(methods=['post'], detail=False)
    def check(self, request):
        p_id = request.GET.get('payment_id')
        payment = PayChecker.objects.get(id=p_id)
        PayHistory.objects.create(
            debtor=payment.debtor,
            som=payment.som,
            dollar=payment.dollar,
            currency=payment.currency,
            comment=payment.comment,
            filial=Filial.objects.first()
        )
        payment.debtor.som -= payment.som
        payment.debtor.dollar -= payment.dollar
        payment.status = True
        payment.save()
        payment.debtor.save()
        return Response({'success':True})
    
import datetime


class PayCheckerViewSet(viewsets.ModelViewSet):
    queryset = PayChecker.objects.all()
    serializer_class = PayCheckerSerializer
    authentication_classes = (MyOwnTokenAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    # def list(self, request):
    #     queryset = self.queryset.filter(agent=request.user, status=False)
    #     return Response(self.serializer_class(queryset, many=True).data)
    def list(self, request):
        debtor_id = request.GET.get('debtor_id')
                
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        today = datetime.date.today()
        
        if debtor_id: 
            if start_date and end_date:
                queryset = self.queryset.filter(date__date__gte=start_date, date__date__lte=end_date, debtor_id=debtor_id)
                return Response(self.serializer_class(queryset, many=True).data)
                
            else:
                queryset = self.queryset.filter(date__date__month=today.month, debtor_id=debtor_id)
                return Response(self.serializer_class(queryset, many=True).data)
        else:
            return Response({'Messages':'please enter ID'})

    def create(self, request):
        agent = request.user
        debtor = request.data['debtor']
        som = request.data['som']
        dollar = request.data['dollar']
        click = request.data['click']
        bank = request.data['bank']
        currency = request.data['currency']
        comment = request.data['comment']
        PayChecker.objects.create(
            agent=agent,
            debtor_id=debtor,
            dollar=dollar,
            som=som,
            currency=currency,
            comment=comment,
            bank=bank,
            click=click,
        )
        return Response({'success': True})


class PayCheckerStatus(viewsets.ModelViewSet):
    queryset = PayChecker.objects.filter(status=False)
    serializer_class = PayCheckerSerializer
    # authentication_classes = (MyOwnTokenAuthentication, TokenAuthentication)
    
    @action(methods=['get'], detail=False)
    def change(self, request):
        pay_id = request.GET.get('pay_id')
        if pay_id:
            try:
                pay = PayChecker.objects.get(id=pay_id)
                pay.status = True
                pay.save()
                return Response({'Messages':'Succeses'})
            except Exception as error:
                return Response({'Messages':'Pay Checke not in data'})
        else:
            return Response({'Messages':'please enter pay_id'})
    


class OrderDesktopViewSet(viewsets.ModelViewSet):
    queryset = MOrder.objects.filter(sold=False)
    serializer_class = MOrderSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @action(methods=['post'], detail=False)
    def sell_order(self, request):
        id = request.GET.get('order_id')
        order = MOrder.objects.get(id=id)
        order.sold = True
        order.save()
        return Response({'success':True})
    
    @action(methods=['post'], detail=False)
    def return_order(self, request):
        id = request.GET.get('order_id')
        order = MOrder.objects.get(id=id)
        order.sold = False
        order.save()
        return Response({'success':True})
