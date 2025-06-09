from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, F
from django.views.generic import TemplateView
from requests import Response
from api.models import *
from django.db.models import Q
from datetime import datetime, date
from django.http.response import HttpResponse, JsonResponse
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
#SMS
from django.conf import settings
from .sms_sender import sendSmsOneContact
import calendar
from django.utils import timezone
from itertools import groupby
from operator import itemgetter



# from django.contrib.auth import authenticate
# user = User.objects.filter(username='max1').last()
# user.set_password(user.password)
# user.save()
# print(user.password)
# u = authenticate(username="max1", password="admin123")
# print(u)

def monthly():
    date = timezone.now()
    year = date.year
    
    if date.month == 12:
        gte = datetime(year, date.month, 1, 0, 0, 0)
        lte = datetime(year + 1, 1, 1, 0, 0, 0)
    else:
        gte = datetime(year, date.month, 1, 0, 0, 0) #2022-03-01 00:00:00
        lte = datetime(year, date.month + 1, 1, 0, 0, 0) #2022-04-01 00:00:00

    return gte, lte

def daily_data():
    # lte = datetime.now() 2022-03-11 11:31:17.107452  
    # gte = lte - timedelta(days=1) 2022-03-10 11:31:17.107452
    # date = timezone.now()
    # year = date.year
    gte = datetime.now().date().replace(day=1)
    lte = datetime.now().date()

    return gte, lte


# def ChartHome(request):

#     year = request.GET.get('year')
#     if not year:
#         year = datetime.today().year
#     else:
#         year = int(year)
#     kirims = []
#     kirimd = []
#     chiqims = []
#     chiqimd = []
#     yalpi = []
#     nasiyas = []
#     filial_sum = []
#     for i in range(1, 13):
#         date = datetime.now().date()
#         if i == 12:
#             month2 = 1
#             year2 = year + 1
#         else:
#             month2 = i + 1
#             year2 = year
#         gte = f'{str(year)}-{str(i)}-01 00:01:00'
#         lte = f'{str(year2)}-{str(month2)}-01 00:01:00'
#         # kirr = Shop.objects.filter(date__gte=gte, date__lte=lte).aggregate(kir = Sum('naqd')+Sum('plastik')+Sum('nasiya'))
#         kirr = Shop.objects.filter(date__gte=gte, date__lte=lte)
#         ks = 0
#         kd = 0
#         filial_count = 0
#         nasiya = 0
#         for kir in kirr:
#             ks += kir.naqd_som + kir.plastik + kir.nasiya_som + kir.transfer + kir.skidka_som
#             filial_count += kir.naqd_som + kir.plastik + kir.nasiya_som + kir.transfer 
#             kd += kir.naqd_dollar + kir.nasiya_dollar + kir.skidka_dollar
#             nasiya += kir.nasiya_som
#         chs = 0
#         chd = 0
#         chiqq = Recieve.objects.filter(date__gte=gte, date__lte=lte)
#         yalpi_mahsulot = Yalpi_savdo.objects.filter(date__gte=gte, date__lte=lte)
#         yalpi_sum = 0
#         for item in yalpi_mahsulot:
#             yalpi_sum += item.total_sum
#         # print(yalpi_sum,"yalpi mahsulot keldi")
#         for chiq in chiqq:
#             chs += chiq.som
#             chd += chiq.dollar
#         kirims.append(ks)
#         kirimd.append(kd)

#         chiqims.append(chs)
#         chiqimd.append(chd)
#         nasiyas.append(nasiya)
#         yalpi.append(yalpi_sum)
#         filial_sum.append(filial_count)
#     dt = {
#         'kirims': kirims,
#         'kirimd': kirimd,
#         'chiqims': chiqims,
#         'chiqimd': chiqimd,
#         'nasiyas': nasiyas,
#         'yalpi':yalpi,
#         'filial_sum':filial_sum
#     }
#     return JsonResponse(dt)


def ChartHome(request):
    year = request.GET.get('year')
    if not year:
        year = datetime.today().year
    else:
        year = int(year)

    valyutas = Valyuta.objects.all()
    valutas_data = []

    for valyuta in valyutas:
        val_id = valyuta.id
        valuta_result = {
            'name': valyuta.name,
            'summas': [],
        }

        for month in range(1, 13):
            if month == 12:
                next_month = 1
                next_year = year + 1
            else:
                next_month = month + 1
                next_year = year

            gte = datetime(year, month, 1)
            lte = datetime(next_year, next_month, 1)

            shops = Shop.objects.filter(date__gte=gte, date__lt=lte, valyuta_id=val_id)
            summa = 0

            for s in shops:
                
                summa += s.total_price

            valuta_result['summas'].append(summa)

        valutas_data.append(valuta_result)

    return JsonResponse({'valutas': valutas_data})


def FilialKirim(request):
    fil1 = []
    fil2 = []
    fil3 = []
    fil4 = []
    fil5 = []
    for i in range(1, 13):
        date = datetime.now()
        year = date.year
        if i == 12:
            month2 = 1
            year2 = year + 1
        else:
            month2 = i + 1
            year2 = year
        # gte = f'{str(year)}-{str(i)}-01 00:01:00'
        # lte = f'{str(year2)}-{str(month2)}-01 00:01:00'
        lte = timezone.now()
        gte = lte - timedelta(days=1)
        a = Shop.objects.filter(date__gte=gte, date__lte=lte).values('filial').annotate(
            som=Sum('naqd_som') + Sum('plastik') + Sum('nasiya_som') + Sum('transfer') + Sum('skidka_som'),
            dollar=Sum('naqd_dollar') + Sum('nasiya_dollar') + Sum('skidka_dollar'))
        try:
            fil1.extend((a[0]['som'], a[0]['dollar']))
        except:
            fil1.append('0')
        try:
            fil2.extend((a[1]['som'], a[1]['dollar']))
        except:
            fil2.append('0')
        try:
            fil3.extend((a[2]['som'], a[2]['dollar']))
        except:
            fil3.append('0')
        try:
            fil4.extend((a[3]['som'], a[3]['dollar']))
        except:
            fil4.append('0')
        try:
            fil5.extend((a[4]['som'], a[4]['dollar']))
        except:
            fil5.append('0')

    dt = {
        # 'data': data,
        'filial1': fil1,
        'filial2': fil2,
        'filial3': fil3,
        'filial4': fil4,
        'filial5': fil5,
    }
    return JsonResponse(dt)


def SalerKirim(request):
    saler1 = []
    saler2 = []
    saler3 = []
    for i in range(1, 13):
        date = datetime.now()
        year = date.year
        if i == 12:
            month2 = 1
            year2 = year + 1
        else:
            month2 = i + 1
            year2 = year
        gte = f'{str(year)}-{str(i)}-01 00:01:00'
        lte = f'{str(year2)}-{str(month2)}-01 00:01:00'
        a = Shop.objects.filter(date__gte=gte, date__lte=lte).values('saler').annotate(
            som=Sum('naqd_som') + Sum('plastik') + Sum('nasiya_som') + Sum('transfer') + Sum('skidka_som'),
            dollar=Sum('naqd_dollar') + Sum('nasiya_dollar') + Sum('skidka_dollar'))
        # try:
        #     saler1.append(a[0]['num'])
        # except:
        #     saler1.append('0')
        # try:
        #     saler2.append(a[1]['num'])
        # except:
        #     saler2.append('0')
        # try:
        #     saler3.append(a[2]['num'])
        # except:
        #     saler3.append('0')
        print(a)
    # print(fil1, fil2, fil3)
    dt = {
        'saler1': saler1,
        'saler2': saler2,
        'saler3': saler3,
    }
    return JsonResponse(dt)


def Summa(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    # if start_date and end_date:
    gte = start_date
    lte = end_date
    # else:
    #     gte, lte = monthly()
    shops = Shop.objects.filter(date__gte=gte, date__lte=lte)
    naqd_som = 0
    naqd_dollar = 0
    plastik = 0
    nasiya_som = 0
    nasiya_dollar = 0
    transfer = 0
    skidka_som = 0
    skidka_dollar = 0
    for shop in shops:
        naqd_som += shop.naqd_som
        naqd_dollar += shop.naqd_dollar
        plastik += shop.plastik
        nasiya_som += shop.nasiya_som
        nasiya_dollar += shop.nasiya_dollar
        transfer += shop.transfer
        skidka_som += shop.skidka_som
        skidka_dollar += shop.skidka_dollar
    som = naqd_som + plastik + nasiya_som + transfer + skidka_som
    dollar = naqd_dollar + plastik + nasiya_dollar + transfer + skidka_dollar

    dt = {
        'naqd_som': naqd_som,
        'naqd_dollar': naqd_dollar,
        'plastik': plastik,
        'nasiya_som': nasiya_som,
        'nasiya_dollar': nasiya_dollar,
        'transfer': transfer,
        'skidka_som': skidka_som,
        'skidka_dollar': skidka_dollar,
        'som': som,
        'dollar': dollar,
    }
    return JsonResponse(dt)


# def Qoldiq(request):
#     fil = Filial.objects.extra(
#         select = {
#             'som':'select sum(api_productfilial.som * api_productfilial.quantity) from api_productfilial where api_productfilial.filial_id = api_filial.id',
#             'dollar':'select sum(api_productfilial.dollar * api_productfilial.quantity) from api_productfilial where api_productfilial.filial_id = api_filial.id'
#         }
#     )
#     fils = []
#     for f in fil:
#         fils.append(f.name)
#     filq = []
#     nol = 0
#     for f in fil:
#         if f.som:
#             filq.append(f.som)
#             filq.append(f.dollar)
#         else:
#             filq.append(nol)
#             filq.append(nol)
#     dt = {
#         'qoldiq':filq,
#         'filial':fils
#     }
#     return JsonResponse(dt)

def DataHome(request):
    data = json.loads(request.body)
    gtes = data['date1']
    ltes = data['date2']
    gte = f'{gtes} 00:01:00'
    lte = f'{ltes} 00:01:00'
    salers = UserProfile.objects.extra(
        select={
            'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
        }
    )
    filials = Filial.objects.extra(
        select={
            'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'pay_som': 'select sum(api_payhistory.som) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                gte, lte),
            'pay_dollar': 'select sum(api_payhistory.dollar) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                gte, lte),
            'yalpi_daromad': 'select sum(api_yalpi_savdo.total_sum) from api_yalpi_savdo where api_yalpi_savdo.filial_id = api_filial.id and api_yalpi_savdo.date > "{}" and api_yalpi_savdo.date < "{}"'.format(
                gte, lte),
        }
    )
    shops = Shop.objects.filter(date__gte=gte, date__lte=lte)
    naqd_som = 0
    naqd_dollar = 0
    plastik = 0
    nasiya_som = 0
    nasiya_dollar = 0
    transfer = 0
    skidka_som = 0
    skidka_dollar = 0
    for shop in shops:
        naqd_som += shop.naqd_som
        naqd_dollar += shop.naqd_dollar
        plastik += shop.plastik
        nasiya_som += shop.nasiya_som
        nasiya_dollar += shop.nasiya_dollar
        transfer += shop.transfer
        skidka_som += shop.skidka_som
        skidka_dollar += shop.skidka_dollar
    som = naqd_som + plastik + nasiya_som + transfer + skidka_som
    dollar = naqd_dollar + plastik + nasiya_dollar + transfer + skidka_dollar

    if som > 0:
        se = []
        for saler in salers:
            s = {
                'name': saler.first_name,
                'staff': saler.staff,
                'filial': saler.filial.name,
                'naqd_som': saler.naqd_som,
                'naqd_dollar': saler.naqd_dollar,
                'plastik': saler.plastik,
                'nasiya_som': saler.nasiya_som,
                'nasiya_dollar': saler.nasiya_dollar,
                'transfer': saler.transfer,
                'skidka_som': saler.skidka_som,
                'skidka_dollar': saler.skidka_dollar,

            }
            se.append(s)
        fl = []
        for filial in filials:
            t = {
                'name': filial.name,
                'naqd_som': filial.naqd_som,
                'naqd_dollar': filial.naqd_dollar,
                'plastik': filial.plastik,
                'nasiya_som': filial.nasiya_som,
                'nasiya_dollar': filial.nasiya_dollar,
                'transfer': filial.transfer,
                'skidka_som': filial.skidka_som,
                'skidka_dollar': filial.skidka_dollar,
                'yalpi_daromad': filial.yalpi_daromad,
            }
            fl.append(t)
        # print(fl,"fl")
        dt1 = {
            'salers': se,
            'filials': fl,
            'naqd_som': naqd_som,
            'naqd_dollar': naqd_dollar,
            'plastik': plastik,
            'nasiya_som': nasiya_som,
            'nasiya_dollar': nasiya_dollar,
            'transfer': transfer,
            'skidka_som': skidka_som,
            'skidka_dollar': skidka_dollar,
        }
    else:
        se = []
        for saler in salers:
            s = {
                'name': saler.first_name,
                'staff': saler.staff,
                'filial': saler.filial.name,
                'naqd_som': 0,
                'naqd_dollar': 0,
                'plastik': 0,
                'nasiya_som': 0,
                'nasiya_dollar': 0,
                'transfer': 0,
                'skidka_som': 0,
                'skidka_dollar': 0,
            }
            se.append(s)
        fl = []
        for filial in filials:
            t = {
                'name': filial.name,
                'naqd_som': 0,
                'naqd_dollar': 0,
                'plastik': 0,
                'nasiya_som': 0,
                'nasiya_dollar': 0,
                'transfer': 0,
                'skidka_som': 0,
                'skidka_dollar': 0,
            }
            fl.append(t)

        dt1 = {
            'salers': se,
            'filials': fl,
            'naqd_som': 0,
            'naqd_dollar': 0,
            'plastik': 0,
            'nasiya_som': 0,
            'nasiya_dollar': 0,
            'transfer': 0,
            'skidka_som': 0,
            'skidka_dollar': 0,
        }
    return JsonResponse(dt1)


def DataWare(request):
    data = json.loads(request.body)
    date1 = data['date1']
    date2 = data['date2']
    wares = Recieve.objects.filter(date__gte=date1, date__lte=date2)
    wr = []
    for w in wares:
        t = {
            'id': w.id,
            'deliver': w.deliver.name,
            'name': w.name,
            'som': w.som,
            'dollar': w.dollar,
            'date': w.date.strftime("%d-%m-%y %I:%M"),
            'sotish_som': w.sum_sotish_som,
            'sotish_dollar': w.sum_sotish_dollar,
            'date': w.date.strftime("%d-%m-%y %I:%M")
        }
        wr.append(t)
    dt1 = {
        'wares': wr
    }
    return JsonResponse(dt1)


def DataWare_html(request):
    data = json.loads(request.body)
    date1 = data['date1']
    date2 = data['date2']
    wares = Recieve.objects.filter(date__date__gte=date1, date__date__lte=date2)
    wr = []
    for w in wares:
        t = {
            'id': w.id,
            'deliver': w.deliver.name,
            'name': w.name,
            'som': w.som,
            'dollar': w.dollar,
            'date': w.date.strftime("%d-%m-%y %I:%M"),
            'sum_sotish_som': w.sum_sotish_som,
            'sum_sotish_dollar': w.sum_sotish_dollar,
            'date': w.date.strftime("%d-%m-%y %I:%M")
        }
        wr.append(t)
    dt1 = {
        'wares': wr
    }
    return render(request, 'omborqabul_ajax.html', dt1)

def return_summa(arr):
    if len(arr) == 0:
        return 0
    return sum(arr)
from itertools import chain

def DebtorHistory(request):
    d_id = request.GET.get('d')
    debtor = Debtor.objects.get(id=d_id)
    pay_history = PayHistory.objects.filter(debtor_id=d_id)
    shop = Shop.objects.filter(debtor_id=d_id, is_finished=True)

    infos = sorted(chain(pay_history, shop), key=lambda instance: instance.date)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        shop = shop.filter(date__date__range=(start_date, end_date))
    context = {
        'shop':shop,
        'debtor': debtor,
        'infos': infos,
        'd_id': debtor.id,
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'debtorhistory.html', context)

def edit_debtor(request, id):
    som = request.POST.get('start_som')
    dollar = request.POST.get('start_dollar')
    date = request.POST.get('start_date')
    Debtor.objects.filter(id=id).update(start_som=som, start_dollar=dollar, start_date=date)
    Debtor.objects.get(id=id).refresh_debt()
    return redirect(request.META['HTTP_REFERER'])

def productinfo(request, id):
    shop = Cart.objects.filter(shop_id=id)
    data = []
    totals = {
        'quantity':0,
        'sotish':0,
        'summa':0,
    }
    for s in shop:
        sotish = s.product.sotish_som  if s.product.sotish_som > 0 else s.product.sotish_dollar
        quantity = s.product.quantity
        summa = sotish * quantity
        totals['sotish'] = sotish 
        totals['quantity'] = quantity 
        totals['summa'] = summa 
        dt = {
            'name': s.product.name,
            'sotish':sotish,
            'valyuta':'UZS'  if s.product.sotish_som > 0 else 'Dollar',
            'quantity':quantity,
            'summa':summa,
            'date':s.date,
        }
        data.append(dt)
   
    context = {
        'products':data,
        'totals':totals,
    }
    return render(request, 'productinfo.html', context)

def product_editing_page(request):
    if request.method == 'POST':
        sotish = request.POST.get('sotish')
        product_id = request.POST.get('product_id')
        # product = ProductFilial.objects.get(id=produt_id)
        # product.sotish_som = sotish
        # product.save()

    context = {
        'product': ProductFilial.objects.all(),
    }
    return render(request, 'product_editing_page.html', context)

def product_editing_search(request):
    search = request.GET.get('search')  
    products = ProductFilial.objects.filter(name__icontains=search)

    data = [
        {
            'product_id': product.id,
            'name': product.name,
            'quantity': product.quantity,
            'price': product.sotish_som, 
        }
        for product in products
    ]

    return JsonResponse(data, safe=False)




from django.db.models import FloatField, IntegerField, F

def filialinfo(request, id):
    filial = Filial.objects.get(id=id)
    shops = Shop.objects.filter(filial=filial)
    incomes = CashboxReceive.objects.filter(filial=filial).order_by('-id')

    date1 = request.GET.get('date1')
    date2 = request.GET.get('date2')
    if date1 and date2:
        shops = shops.filter(date__range=(date1, date2))
        incomes = incomes.filter(date__range=(date1, date2))

    total_income = incomes.filter(status='accepted').aggregate(
        foo=Coalesce(Sum("total_sum"), float(0), output_field=FloatField()))['foo']
    total_shop = shops.all().aggregate(foo=Coalesce(Sum(
        F("naqd_dollar") + F("transfer") + F("plastik") +
        F("nasiya_dollar") - F("skidka_dollar")
    ), float(0), output_field=FloatField()))['foo']
    
    farq = total_shop - total_income

    context = {
        'fil': filial,
        'filial': "active",
        'filial_t': "true",
        'incomes': incomes,
        'total_income': total_income,
        'total_shop': total_shop,
        'farq': farq
    }
    return render(request, 'filialinfo.html', context)

    # if request.method == 'POST':
    #     filial_kirim_dollar = request.POST.get('filial_kirim_dollar')
    #     filial_kirim_som = request.POST.get('filial_kirim_som')
    #     filial_id = request.POST.get('filial_id')
    #     kassa_var = Kassa.objects.first()

    #     filial = Filial.objects.get(id=filial_id)

    #     if filial.qarz_som:
    #         filial.qarz_som -= int(filial_kirim_som)
    #         filial.savdo_puli_som -= int(filial_kirim_som)
    #         kassa_var.som += int(filial_kirim_som)

    #     if filial.qarz_dol:    
    #         filial.qarz_dol -= int(filial_kirim_dollar)
    #         filial.savdo_puli_dol -= int(filial_kirim_dollar)
    #         kassa_var.dollar += int(filial_kirim_dollar)

    #     filial.save()
    #     kassa_var.save()

    #     return redirect(f'/filialinfo/{id}')

    # filial = Filial.objects.get(id=id)
    # products = ProductFilial.objects.all()
    # qoldiq_som = 0
    # qoldiq_dol = 0

    # for product in products:

    #     qoldiq_som += product.quantity * product.som
    #     qoldiq_dol += product.quantity * product.dollar
    # #shop kunlik savdolar 30kunlik (zarur bulgani uchun bu yul tutildi)
    # day = timezone.now()
    # thirty_day_ago = day - timedelta(days=30)
    # shops = Shop.objects.filter(date__gte = thirty_day_ago)
    # data = []
    # for i in range(1,30):
    #     kun = day - timedelta(days=i)
    #     shop_som = shops.filter(date__date = kun.date()).aggregate(Sum('naqd_som'))['naqd_som__sum']
    #     shop_dol = shops.filter(date__date = kun.date()).aggregate(Sum('naqd_dollar'))['naqd_dollar__sum']
    #     shop_pla = shops.filter(date__date = kun.date()).aggregate(Sum('plastik'))['plastik__sum']
    #     shop_tra = shops.filter(date__date = kun.date()).aggregate(Sum('transfer'))['transfer__sum']
    #     dt = {
    #         'date': kun,
    #         'som': shop_som,
    #         'shop_dol': shop_dol,
    #         'shop_pla': shop_pla,
    #         'shop_tra': shop_tra,
    #     }
    #     data.append(dt)

    # context = {
    #     'data':data,
    #     'fil':filial,
    #     'qoldiq_som':qoldiq_som,
    #     'qoldiq_dol':qoldiq_dol,
    #     'filial': "active",
    #     'filial_t': "true"
    # }
    # context['dollar_kurs'] = Course.objects.last().som

def edit_deliver_history(request):
    id = request.POST.get('history_id')
    debt_changed_som = request.POST.get('debt_som')
    debt_changed_dollar = request.POST.get('debt_dollar')
    
    debt = DebtDeliver.objects.get(id=id)
    if debt_changed_som:
        debt.som = debt_changed_som
    if debt_changed_dollar:
        debt.dollar = debt_changed_dollar
    debt.save()
    return redirect(request.META['HTTP_REFERER'])


def DeliverHistory(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    gte, lte = monthly()
    d_id = request.GET.get('d')
    pays = DeliverPayHistory.objects.filter(deliver_id=d_id)
    debts = DebtDeliver.objects.filter(deliver_id=d_id)
    dollar_kurs = Course.objects.last().som
    psom = 0
    pdollar = 0
    dsom = 0
    ddollar = 0
    for p in pays:
        psom += p.som
        psom += (p.dollar * dollar_kurs)
        # pdollar += p.dollar
    for d in debts:
        dsom += d.som
        dsom += d.dollar * dollar_kurs
        # ddollar += d.dollar
    
    all_som = dsom + psom

    # all_dollar = ddollar + pdollar
    


    context = {
        'psom': psom,
        'pdollar': pdollar,
        'dsom': all_som,
        # 'ddollar': all_dollar,
        'pays': pays,
        'debts': debts,
        'd_id': d_id,
        'deliver': "active",
        'deliver_t': "true",
        'money_circulation':MoneyCirculation.objects.filter(is_delete=False),
        'valyuta':Valyuta.objects.all(),
    
    }


    payments = DeliverPayments.objects.filter(deliver_id=d_id).last().payments.all()

    if start_date and end_date:
        payments = payments.filter(date__date__gte=start_date, date__date__lte=end_date)
    else:
        payments = payments.filter(date__date__gte=datetime.now().date().replace(day=1))
    
    context['payments'] = payments
    context['dollar_kurs'] = Course.objects.last().som
    return render(request, 'deliverhistory.html', context)

from django.db.models.functions import Cast, Coalesce

def filial_chiqim_view(request):
    expenses = FilialExpense.objects.all()
    branches = Filial.objects.all()

    date1 = request.GET.get('date1')
    date2 = request.GET.get('date2')
    filial_name = request.GET.get('filial-name')
    current_filial = 'Barcha filiallar'

    if date1 and date2:
        expenses = expenses.filter(created_at__range=(date1, date2))

    if filial_name:
        current_filial = filial_name
        if filial_name != 'Barcha filiallar':
            expenses = expenses.filter(filial__name=filial_name)

    total_expenses = expenses.aggregate(foo=Coalesce(
        Sum('total_sum'),
        0
    ))['foo']

    context = {
        'filial': "active",
        'filial_t': "true",
        'filials': branches,
        'current_filial': current_filial,
        'total_expenses': total_expenses,
        'expenses': expenses,
    }

    return render(request, 'filial_chiqim.html', context)





def NasiyaTarix(request):
    data = json.loads(request.body)
    
    date1 = data['date1']
    date2 = data['date2']
    d_id = data['d_id']
    pays = DeliverPayHistory.objects.filter(date__gte=date1, date__lte=date2, deliver_id=d_id)
    debts = DebtDeliver.objects.filter(date__gte=date1, date__lte=date2, deliver_id=d_id)

    print(debts)
    psom = 0
    pdollar = 0
    dsom = 0
    ddollar = 0
    for p in pays:
        psom += p.som
        pdollar += p.dollar
    for d in debts:
        dsom += d.som
        ddollar += d.dollar
    pay = []
    for w in pays:
        print("p")
        t = {
            # 'id': w.id,
            'som': w.som,
            'dollar': w.dollar,
            'date': w.date.strftime("%d-%m-%y %I:%M"),
        }
        pay.append(t)
    debt = []
    for w in debts:
        print("d")
        t = {
            # 'id': w.id,
            'som': w.som,
            'dollar': w.dollar,
            'date': w.date,
        }
        debt.append(t)
    dt1 = {
        'psom': psom,
        'pdollar': pdollar,
        'dsom': dsom+psom,
        'ddollar': ddollar,
        'pays': pay,
        'debts': debt,
    }
    return JsonResponse(dt1)


def     kurs_page(request):
    if request.method == 'POST':
        kurs = request.POST.get('kurs')
        kurs_baza = 0
        try:
            kurs_baza = Exchange.objects.first()
            kurs = float(kurs)
            kurs_baza.kurs = kurs
            kurs_baza.save()
        except:
            pass
        return render(request, 'change_kurs_page.html', {'kurs': kurs_baza, 'dollar_kurs': Course.objects.last().som})
    else:
        kurs = Exchange.objects.first()
        return render(request, 'change_kurs_page.html', {'kurs': kurs, 'dollar_kurs': Course.objects.last().som})


def add_tolov(request):
    
    deliver_id = request.POST.get('deliver_id')
    som = request.POST.get('som')
    izoh = request.POST.get('izoh')
    dollor = request.POST.get('dollor')
    turi = request.POST.get('turi')
    money_circulation = request.POST.get('money_circulation')
    valyuta = request.POST.get('valyuta')
    type = int(request.POST.get('type'))

    kassa = Kassa.objects.first()
    kurs = Course.objects.last()
    if type == 1 and turi == 'Naqd':
        if kassa.som < float(som) or kassa.dollar < float(dollor):
            messages.info(request, f'Kassada mablag\' yetarli emas.')
            return redirect("/deliverhistory/?d=" + str(deliver_id))
    
    # kassa.som -= float(som)
    # kassa.dollar -= float(dollor)
    if type == 1:
        chiqim = Chiqim.objects.create(izox=izoh, deliver_id=deliver_id)
        # Naqd
        # Plastik
        # Pul o'tkazish
        # if som and kassa.som >= int(som):
        if turi == 'Naqd' and kassa.som >= int(som):
            chiqim.kassa_som_eski = kassa.som
            chiqim.qancha_som = som
            kassa.som -= float(som)
            chiqim.kassa_som_yangi = kassa.som
        elif turi == 'Plastik' and kassa.plastik >= int(som):
            chiqim.kassa_plastik_eski = kassa.plastik
            chiqim.plastik = som
            kassa.plastik -= float(som)
            chiqim.kassa_plastik_yangi = kassa.plastik
        elif turi == "Pul o'tkazish" and kassa.hisob_raqam >= int(som):
            chiqim.kassa_hisob_raqam_eski = kassa.hisob_raqam
            chiqim.qancha_hisob_raqamdan = som
            kassa.hisob_raqam -= float(som)
            chiqim.kassa_hisob_raqam_yangi = kassa.hisob_raqam
                
        
        if dollor and kassa.dollar >= int(dollor):
            if turi == 'Naqd':
                chiqim.kassa_dol_eski = kassa.dollar
                chiqim.qancha_dol = dollor
                kassa.dollar -= float(dollor)
                chiqim.kassa_dol_yangi = kassa.dollar
            

        # if dollor and kassa.dollar >= int(dollor):
        #     chiqim.kassa_dol_eski = kassa.dollar
        #     chiqim.qancha_dol = dollor
        #     chiqim.kassa_dol_yangi = kassa.dollar
    
    
        kassa.save()
        chiqim.save()

    ht = DeliverPayHistory.objects.create(deliver_id=deliver_id, som=som, dollar=dollor, turi=turi, izoh=izoh, kurs=kurs.som,
                                          money_circulation_id=money_circulation,valyuta_id=valyuta,)
    
    if type == 1:
        chiqim.deliverpayment = DeliverPaymentsAll.objects.filter(deliverpayments__deliver_id=deliver_id).order_by('id').last()
        chiqim.save()
    url = "/deliverhistory/?d=" + str(deliver_id)
    return redirect(url)


def GetItem(request):
    data = json.loads(request.body)
    id = data['id']
    items = RecieveItem.objects.filter(recieve_id=id)
    it = []
    for i in items:
        its = {
            'id': i.id,
            'product': i.product.name,
            'som': i.som,
            'dollar': i.dollar,
            'kurs': i.kurs,
            'quantity': i.quantity
        }
        it.append(its)
    dt1 = {
        'items': it
    }
    return JsonResponse(dt1)

def GetItem_html(request):
    data = json.loads(request.body)
    id = data['id']
    items = RecieveItem.objects.filter(recieve_id=id)
    it = []
    for i in items:
        its = {
            'id': i.id,
            'product': i.product.name,
            'som': i.som,
            'dollar': i.dollar,
            'kurs': i.kurs,
            'quantity': i.quantity
        }
        it.append(its)
    dt1 = {
        'items': it
    }
    return JsonResponse(dt1)


# class Home(LoginRequiredMixin, TemplateView):
#     template_name = 'home.html'

#     def get_context_data(self, **kwargs):
#         gte, lte = daily_data() #

#         year = self.request.GET.get('year', datetime.now().year)
#         start_date = self.request.GET.get('start_date', None)
#         end_date = self.request.GET.get('end_date', None)
        
#         if start_date and end_date:
#             gte = datetime.strptime(start_date, '%Y-%m-%d').date()

#             lte = datetime.strptime(end_date, '%Y-%m-%d').date()


#         # else:
#         #     gte = datetime.now().date().replace(day=1)
#         #     lte = datetime.now().date()

#         try:
#             salers = UserProfile.objects.extra(
#                 select={
#                     'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
                    
#                 }
#             )
#             filials = Filial.objects.extra(
#                 select={
#                     'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
#                         gte, lte),
#                     'pay_som': 'select sum(api_payhistory.som) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
#                         gte, lte),
#                     'pay_dollar': 'select sum(api_payhistory.dollar) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
#                         gte, lte),
#                     'yalpi_daromad': 'select sum(api_yalpi_savdo.total_sum) from api_yalpi_savdo where api_yalpi_savdo.filial_id = api_filial.id and api_yalpi_savdo.date > "{}" and api_yalpi_savdo.date < "{}"'.format(
#                         gte, lte),
#                 }
#             )
#         except Exception as e:
#             return HttpResponse(str(e),"nima bu")


#         top_debtors = (
#             PayHistory.objects
#             .values('debtor', 'debtor__fio') 
#             .annotate(total_som=Sum('som'), total_dollar=Sum('dollar')) 
#             .order_by('-total_som', '-total_dollar')[:10]  
#         )
#         top_products = (
#             Cart.objects
#             .values('product__name')
#             .annotate(total_quantity=Sum('quantity'))
#             .order_by('-total_quantity')[:10]
#         )

#         top_products_profit = (
#             Cart.objects
#             .values('product__name')
#             .annotate(
#                 total_profit_som=Sum(F('quantity') * (F('product__sotish_som') - F('product__som'))),
#                 total_profit_dollar=Sum(F('quantity') * (F('product__sotish_dollar') - F('product__dollar')))
#             )
#             .order_by('-total_profit_som', '-total_profit_dollar')[:10] 
#         )

#         shops = Shop.objects.filter(date__gte=gte, date__lte=lte)
#         naqd_som = 0
#         naqd_dollar = 0
#         plastik = 0
#         nasiya_som = 0
#         nasiya_dollar = 0
#         transfer = 0
#         skidka_som = 0
#         skidka_dollar = 0
#         for shop in shops:
#             naqd_som += shop.naqd_som
#             naqd_dollar += shop.naqd_dollar
#             plastik += shop.plastik
#             nasiya_som += shop.nasiya_som
#             nasiya_dollar += shop.nasiya_dollar
#             transfer += shop.transfer
#             skidka_som += shop.skidka_som
#             skidka_dollar += shop.skidka_dollar
#         som = naqd_som + plastik + nasiya_som + transfer + skidka_som
#         dollar = naqd_dollar + plastik + nasiya_dollar + transfer + skidka_dollar

#         jami = 0
#         try:
#             for f in filials:
                
#                 if f.naqd_som is None:
#                     f.naqd_som = 0
#                 if f.plastik is None:
#                     f.plastik = 0
#                 if f.nasiya_som is None:
#                     f.nasiya = 0
#                 jami += int(f.naqd_som) + int(f.plastik) + int(f.nasiya_som)
#         except Exception as e:
#             print(e,"nonemi bu")

        
#         context = super().get_context_data(**kwargs)
#         context['home'] = 'active'
#         context['valyuta'] = Valyuta.objects.all()
#         context['home_t'] = 'true'
#         context['salers'] = salers
#         context['sellers'] = salers.filter(staff=3)
#         context['filials'] = filials
#         context['jamisum'] = jami
#         context['top_debtors'] = top_debtors
#         context['top_products'] = top_products
#         context['top_products_profit'] = top_products_profit

#         context['filters'] = {
#             'year':year,
#             'start_date':gte,
#             'end_date':lte,
#         }

#         if som != 0:
#             context['naqd_som'] = naqd_som
#             context['naqd_dollar'] = naqd_dollar
#             context['plastik'] = plastik
#             context['nasiya_som'] = nasiya_som
#             context['nasiya_dollar'] = nasiya_dollar
#             context['transfer'] = transfer
#             context['skidka_som'] = skidka_som
#             context['skidka_dollar'] = skidka_dollar
#         else:
#             context['naqd_som'] = 0
#             context['naqd_dollar'] = 0
#             context['plastik'] = 0
#             context['nasiya_som'] = 0
#             context['nasiya_dollar'] = 0
#             context['transfer'] = 0
#             context['skidka_som'] = 0
#             context['skidka_dollar'] = 0
#             context['dollar_kurs'] = Course.objects.last().som
#         return context


# class Home(LoginRequiredMixin, TemplateView):
#     template_name = 'home.html'

#     def get_context_data(self, **kwargs):
#         gte, lte = daily_data() #
#         valyutas = Valyuta.objects.all()

#         year = self.request.GET.get('year', datetime.now().year)
#         start_date = self.request.GET.get('start_date', None)
#         end_date = self.request.GET.get('end_date', None)
        
#         if start_date and end_date:
#             gte = datetime.strptime(start_date, '%Y-%m-%d').date()

#             lte = datetime.strptime(end_date, '%Y-%m-%d').date()


#         # else:
#         #     gte = datetime.now().date().replace(day=1)
#         #     lte = datetime.now().date()

#         salers = UserProfile.objects.all()
            


#         # top_debtors = Debtor.objects.all()

#         # for i in top_debtors:
#         #     i.valutas = i.debt_haqimiz

#         top_debtors_per_currency = []
#         top_creditors_per_currency = []

#         for valyuta in Valyuta.objects.all():
#             # Qarzdorlar (summa < 0)
#             top_debtors = (
#                 Wallet.objects
#                 .filter(valyuta=valyuta, summa__lt=0, customer__isnull=False)
#                 .values('customer__id', 'customer__fio')
#                 .annotate(total_debt=Sum('summa'))
#                 .order_by('total_debt')[:10]
#             )
#             top_debtors_per_currency.append({
#                 'valyuta': valyuta,
#                 'debtors': list(top_debtors)
#             })

#             # Haqqi borlar (summa > 0)
#             top_creditors = (
#                 Wallet.objects
#                 .filter(valyuta=valyuta, summa__gt=0, customer__isnull=False)
#                 .values('customer__id', 'customer__fio')
#                 .annotate(total_credit=Sum('summa'))
#                 .order_by('-total_credit')[:10]
#             )
            
#             top_creditors_per_currency.append({
#                 'valyuta': valyuta,
#                 'creditors': list(top_creditors)
#             })





#         top_sell_products = (
#             Cart.objects
#             .values('product__name')
#             .annotate(total_quantity=Sum('quantity'))
#             .order_by('-total_quantity')[:10]
#         )

#         top_products_profit = []

#         # 3. Ushbu maksimal summaga mos keladigan mahsulotlarni topamiz
        
#         aggregated = (
#             Cart.objects
#             .values('shop__valyuta', 'shop__valyuta_id', 'product__id', 'product__name')  # Added 'shop__valyuta_id' here
#             .annotate(
#                 total_sum=Coalesce(
#                     Sum('summa_total', output_field=FloatField()), 
#                     Value(0.0, output_field=FloatField())
#                 )
#             )
#         )


#         # top_profit_product = []

#         # for valyuta_obj in valyutas:
#         #     valyuta_name = valyuta_obj.name
#         #     valyuta_id = valyuta_obj.id

#         #     currency_products = [
#         #         p for p in aggregated 
#         #         if p.get('shop__valyuta') is not None and p['shop__valyuta_id'] == valyuta_id
#         #     ]

#         #     if not currency_products:
#         #         continue

#         #     # Eng yuqori 10 mahsulotni total_sum bo‘yicha tartiblash
#         #     top_products_raw = sorted(currency_products, key=lambda p: p['total_sum'], reverse=True)[:10]

#         #     # Faol ro‘yxatga tushirish
#         #     top_products = [
#         #         {
#         #             'product_id': p['product__id'],
#         #             'product': p['product__name'],
#         #             'summa': p['total_sum']
#         #         }
#         #         for p in top_products_raw
#         #     ]

#         #     top_profit_product.append({
#         #         'valyuta': valyuta_name,
#         #         'products': top_products
#         #     })

#         aggregated = (
#             Cart.objects
#             .values(
#                 'shop__valyuta',
#                 'shop__valyuta_id',
#                 'shop__saler_id',
#                 'product__id',
#                 'product__name'
#             )
#             .annotate(
#                 total_sum=Coalesce(
#                     Sum('summa_total', output_field=FloatField()),
#                     Value(0.0, output_field=FloatField())
#                 )
#             )
#         )

#         top_profit_product = []

#         for valyuta_obj in valyutas:
#             valyuta_name = valyuta_obj.name
#             valyuta_id = valyuta_obj.id

#             currency_products = [
#                 p for p in aggregated 
#                 if p.get('shop__valyuta') is not None and p['shop__valyuta_id'] == valyuta_id
#             ]

#             if not currency_products:
#                 continue

#             top_products_raw = sorted(currency_products, key=lambda p: p['total_sum'], reverse=True)[:10]

#             top_products = [
#                 {
#                     'product_id': p['product__id'],
#                     'product': p['product__name'],
#                     'summa': p['total_sum']
#                 }
#                 for p in top_products_raw
#             ]

#             top_profit_product.append({
#                 'valyuta': valyuta_name,
#                 'products': top_products
#             })

        
#         aggregated_salers = (
#             Cart.objects
#             .values('shop__valyuta', 'shop__valyuta_id', 'shop__saler_id')
#             .annotate(
#                 total_sum=Coalesce(
#                     Sum('summa_total', output_field=FloatField()),
#                     Value(0.0, output_field=FloatField())
#                 )
#             )
#         )

#         saler_map = {
#             saler.id: str(saler)  # yoki saler.full_name, saler.user.username
#             for saler in UserProfile.objects.all()
#         }

#         # 2. Har bir valyuta va sotuvchi bo‘yicha umumiy summa hisoblash
#         aggregated_salers = (
#             Cart.objects
#             .exclude(shop__saler__isnull=True)
#             .values('shop__valyuta', 'shop__valyuta_id', 'shop__saler_id')
#             .annotate(
#                 total_sum=Coalesce(
#                     Sum('summa_total', output_field=FloatField()),
#                     Value(0.0, output_field=FloatField())
#                 )
#             )
#         )

#         # 3. Top 10 sotuvchi har bir valyuta bo‘yicha
#         aggregated_salers = (
#             Cart.objects
#             .values('shop__valyuta', 'shop__valyuta_id', 'shop__saler', 'shop__saler_id')
#             .annotate(total_sum=Coalesce(Sum('summa_total', output_field=FloatField()), 0))
#         )

#         # Saler ma'lumotlarini olish (id => name)
#         saler_map = {
#             s.id: str(s)  # yoki s.full_name yoki s.user.username
#             for s in UserProfile.objects.filter(id__in=[row['shop__saler_id'] for row in aggregated_salers])
#         }

#         top_salers_by_valyuta = []

#         for valyuta_obj in valyutas:
#             valyuta_id = valyuta_obj.id
#             valyuta_name = valyuta_obj.name

#             saler_entries = [
#                 entry for entry in aggregated_salers
#                 if entry['shop__valyuta_id'] == valyuta_id
#             ]

#             if not saler_entries:
#                 continue

#             # Eng yuqori 10 ta sotuvchini olish
#             top_salers_raw = sorted(saler_entries, key=lambda x: x['total_sum'], reverse=True)[:10]

#             top_salers = []
#             for s in top_salers_raw:
#                 saler_id = s['shop__saler_id']
#                 saler_name = saler_map.get(saler_id, "Noma'lum")

#                 top_salers.append({
#                     'saler_id': saler_id,
#                     'saler_name': saler_name,
#                     'summa': s['total_sum']
#                 })

#             top_salers_by_valyuta.append({
#                 'valyuta': valyuta_name,
#                 'salers': top_salers
#             })

#                 # top_profit_by_saler.append(saler_entry)
        
#         # [
#         #     "saler_id": 1,
#         #     "saler_name": 1,
#         #     "saler_id": 1,
#         #     "saler_id": 1,
#         #     "saler_id": 1,
#         # ]


#         # shops = Shop.objects.filter(date__gte=gte, date__lte=lte)
#         # naqd_som = 0
#         # naqd_dollar = 0
#         # plastik = 0
#         # nasiya_som = 0
#         # nasiya_dollar = 0
#         # transfer = 0
#         # skidka_som = 0
#         # skidka_dollar = 0
#         # for shop in shops:
#         #     naqd_som += shop.naqd_som
#         #     naqd_dollar += shop.naqd_dollar
#         #     plastik += shop.plastik
#         #     nasiya_som += shop.nasiya_som
#         #     nasiya_dollar += shop.nasiya_dollar
#         #     transfer += shop.transfer
#         #     skidka_som += shop.skidka_som
#         #     skidka_dollar += shop.skidka_dollar
#         # som = naqd_som + plastik + nasiya_som + transfer + skidka_som
#         # dollar = naqd_dollar + plastik + nasiya_dollar + transfer + skidka_dollar

#         # jami = 0
#         # try:
#         #     for f in filials:
                
#         #         if f.naqd_som is None:
#         #             f.naqd_som = 0
#         #         if f.plastik is None:
#         #             f.plastik = 0
#         #         if f.nasiya_som is None:
#         #             f.nasiya = 0
#         #         jami += int(f.naqd_som) + int(f.plastik) + int(f.nasiya_som)
#         # except Exception as e:
#         #     print(e,"nonemi bu")

#         context = super().get_context_data(**kwargs)
#         context['home'] = 'active'
#         context['valyuta'] = valyutas
#         context['top_debtors_per_currency'] = top_debtors_per_currency
#         context['top_creditors_per_currency'] = top_creditors_per_currency
#         context['top_salers_by_valyuta'] = top_salers_by_valyuta
#         context['home_t'] = 'true'
#         context['salers'] = salers
#         context['sellers'] = salers.filter(staff=3)
#         context['top_profit_product'] = top_profit_product
#         # context['jamisum'] = jami
#         context['top_debtors'] = top_debtors
#         context['top_sell_products'] = top_sell_products
#         context['top_products_profit'] = top_products_profit

#         context['filters'] = {
#             'year':year,
#             'start_date':gte,
#             'end_date':lte,
#         }

#         # if som != 0:
#         #     context['naqd_som'] = naqd_som
#         #     context['naqd_dollar'] = naqd_dollar
#         #     context['plastik'] = plastik
#         #     context['nasiya_som'] = nasiya_som
#         #     context['nasiya_dollar'] = nasiya_dollar
#         #     context['transfer'] = transfer
#         #     context['skidka_som'] = skidka_som
#         #     context['skidka_dollar'] = skidka_dollar
#         # else:
#         #     context['naqd_som'] = 0
#         #     context['naqd_dollar'] = 0
#         #     context['plastik'] = 0
#         #     context['nasiya_som'] = 0
#         #     context['nasiya_dollar'] = 0
#         #     context['transfer'] = 0
#         #     context['skidka_som'] = 0
#         #     context['skidka_dollar'] = 0
#         #     context['dollar_kurs'] = Course.objects.last().som
#         return context


class Home(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        from django.db.models import Sum, FloatField, Value
        from django.db.models.functions import Coalesce

        gte, lte = daily_data()

        # Foydalanuvchi filtrlarini olish
        year = self.request.GET.get('year', datetime.now().year)
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if start_date and end_date:
            gte = datetime.strptime(start_date, '%Y-%m-%d').date()
            lte = datetime.strptime(end_date, '%Y-%m-%d').date()
            shops = Shop.objects.filter(date__date__gte=gte, date__date__lte=lte)
        else: 
            shops = Shop.objects.filter(date__date__gte=datetime.now().date().replace(day=1))

        valyutas = Valyuta.objects.all()
        salers = UserProfile.objects.all()
        

        # =============================
        # 1. Top 10 qarzdor va haqqi borlar
        # =============================
        top_debtors_per_currency = []
        top_creditors_per_currency = []

        for valyuta in valyutas:
            # Qarzdorlar (summa < 0)
            debtors = (
                Wallet.objects
                .filter(valyuta=valyuta, summa__lt=0, customer__isnull=False)
                .values('customer__id', 'customer__fio')
                .annotate(total_debt=Sum('summa'))
                .order_by('total_debt')[:10]
            )
            top_debtors_per_currency.append({
                'valyuta': valyuta,
                'debtors': list(debtors)
            })

            # Haqqi borlar (summa > 0)
            creditors = (
                Wallet.objects
                .filter(valyuta=valyuta, summa__gt=0, customer__isnull=False)
                .values('customer__id', 'customer__fio')
                .annotate(total_credit=Sum('summa'))
                .order_by('-total_credit')[:10]
            )
            top_creditors_per_currency.append({
                'valyuta': valyuta,
                'creditors': list(creditors)
            })

        # =============================
        # 2. Eng ko‘p sotilgan mahsulotlar
        # =============================
        top_sell_products = (
            Cart.objects.filter(shop__in=shops)
            .values('product__name')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')[:10]
        )

        # =============================
        # 3. Har valyuta bo‘yicha eng ko‘p foyda keltirgan mahsulotlar
        # =============================
        aggregated_products = (
            Cart.objects.filter(shop__in=shops)
            .values('shop__valyuta_id', 'product__id', 'product__name')
            .annotate(
                total_sum=Coalesce(Sum('summa_total', output_field=FloatField()), Value(0.0))
            )
        )

        top_profit_product = []
        for valyuta in valyutas:
            filtered = [
                p for p in aggregated_products
                if p['shop__valyuta_id'] == valyuta.id
            ]
            top_10 = sorted(filtered, key=lambda x: x['total_sum'], reverse=True)[:10]
            top_profit_product.append({
                'valyuta': valyuta.name,
                'products': [
                    {
                        'product_id': p['product__id'],
                        'product': p['product__name'],
                        'summa': p['total_sum']
                    } for p in top_10
                ]
            })

        # =============================
        # 4. Har valyuta bo‘yicha eng ko‘p sotgan sotuvchilar
        # =============================
        aggregated_salers = (
            Cart.objects.filter(shop__in=shops)
            .exclude(shop__saler__isnull=True)
            .values('shop__valyuta_id', 'shop__saler_id')
            .annotate(total_sum=Coalesce(Sum('summa_total', output_field=FloatField()), Value(0.0)))
        )

        saler_map = {
            saler.id: str(saler)
            for saler in UserProfile.objects.filter(id__in=[row['shop__saler_id'] for row in aggregated_salers])
        }

        top_salers_by_valyuta = []
        for valyuta in valyutas:
            filtered = [
                row for row in aggregated_salers
                if row['shop__valyuta_id'] == valyuta.id
            ]
            top_10 = sorted(filtered, key=lambda x: x['total_sum'], reverse=True)[:10]
            top_salers_by_valyuta.append({
                'valyuta': valyuta.name,
                'salers': [
                    {
                        'saler_id': row['shop__saler_id'],
                        'saler_name': saler_map.get(row['shop__saler_id'], 'Noma\'lum'),
                        'summa': row['total_sum']
                    }
                    for row in top_10
                ]
            })

        # =============================
        # 5. Kontekstga hammasini joylash
        # =============================
        context = super().get_context_data(**kwargs)
        context.update({
            'home': 'active',
            'home_t': 'true',
            'valyuta': valyutas,
            'salers': salers,
            'sellers': salers.filter(staff=3),
            'top_debtors_per_currency': top_debtors_per_currency,
            'top_creditors_per_currency': top_creditors_per_currency,
            'top_sell_products': top_sell_products,
            'top_profit_product': top_profit_product,
            'top_salers_by_valyuta': top_salers_by_valyuta,
            'filters': {
                'year': year,
                'start_date': gte,
                'end_date': lte,
            }
        })

        return context


class LTV(LoginRequiredMixin, TemplateView):
    template_name = 'LTV.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ltv'] = 'active'
        context['ltv_t'] = 'true'
        context['dollar_kurs'] = Course.objects.last().som
        
        return context
# get ajax LTV datas 
def get_ltv_data(request):
    try:
        #time
        day = datetime.now()
        month = day.month
        year = day.year

        date_start = request.GET.get('start')
        date_end = request.GET.get('end')

        if month == 12:
            month2 = 1
            year2 = year + 1
        else:
            month2 = month + 1
            year2 = year
       

        ll = []
        if date_start is not None and date_end is not None:
            debrors = Debtor.objects.filter(date__gte=date_start, date__lte=date_end)
            debtor_pay_history = PayHistory.objects.filter(date__gte=date_start, date__lte=date_end)
        else:
            debrors = Debtor.objects.filter(date__month=month, date__year=year)
            debtor_pay_history = PayHistory.objects.filter(date__month=month, date__year=year)
        productfilials = ProductFilial.objects.all()

        all_clint_qarz_som = 0
        # all_clint_qarz_dollar = 0

        all_clint_tulagan_som = 0
        # all_clint_tulagan_dollar = 0

        all_clint_qarz_qoldiq_som = 0
        # all_clint_qarz_qoldiq_dollar = 0

        all_clint_daromad_som = 0
        # all_clint_daromad_dollar = 0
        for debror in debrors:
            qarz_sum = debror.som
            total_tulagan_som = debtor_pay_history.filter(debtor_id=debror.id).aggregate(Sum('som'))['som__sum']
            total_olgan_tavar_sum = productfilials.filter(filial__filial_pay__debtor_id=debror.id).aggregate(Sum('sotish_som'))['sotish_som__sum']
            total_olgan_tavar_kelish_sum = productfilials.filter(filial__filial_pay__debtor_id=debror.id).aggregate(Sum('som'))['som__sum']
            
            
            # qarz_dollar = debror.dollar
            #tulanganlari
            # total_tulagan_dollar = debtor_pay_history.filter(debtor_id=debror.id).aggregate(Sum('dollar'))['dollar__sum']
            
            # mijoz olgan tavarlar total sotish summasi
            # total_olgan_tavar_dollar = productfilials.filter(filial__filial_pay__debtor_id=debror.id).aggregate(Sum('sotish_dollar'))['sotish_dollar__sum']
            #mijoz olgan avarlar total kelish summasi
            # total_olgan_tavar_kelish_dollar = productfilials.filter(filial__filial_pay__debtor_id=debror.id).aggregate(Sum('dollar'))['dollar__sum']
            # if qarz_sum is None or qarz_dollar is None or total_tulagan_som is None or total_olgan_tavar_sum is None or total_olgan_tavar_dollar is None or total_tulagan_dollar is None or total_olgan_tavar_kelish_sum is None or total_olgan_tavar_kelish_dollar is None:
            
            if qarz_sum == None: 
                qarz_sum = 0
                
            if total_tulagan_som == None:
                total_tulagan_som = 0
                
            if total_olgan_tavar_sum == None:
                total_olgan_tavar_sum = 0
                
            if total_olgan_tavar_kelish_sum == None:
                total_olgan_tavar_kelish_sum = 0
            # if qarz_dollar == None:
            #     qarz_dollar = 0
                
                
            # if total_olgan_tavar_dollar == None:
            #     total_olgan_tavar_dollar = 0
                
            # if total_tulagan_dollar == None:
            #     total_tulagan_dollar = 0
            
            
            # if total_olgan_tavar_kelish_dollar == None:
            #     total_olgan_tavar_kelish_dollar = 0
                
                # if total_tulagan_dollar == None:
                #     total_tulagan_dollar = 0
                # qoldiq_qarz_sum = 0
                # qoldiq_qarz_dollar = 0
                # mijozdan_daromad_sum = 0
                # mijozdan_daromad_dollar = 0
                
                # all_clint_qarz_som += qarz_sum
                # all_clint_qarz_dollar += qarz_dollar
                # all_clint_tulagan_som += 0
                # all_clint_tulagan_dollar += 0
                
                
            # else:
                #qarz
            qoldiq_qarz_sum = float(qarz_sum) - float(total_tulagan_som)
            
            mijozdan_daromad_sum = float(total_olgan_tavar_sum) - float(total_olgan_tavar_kelish_sum)
            # qoldiq_qarz_dollar = float(qarz_dollar) - float(total_tulagan_dollar)
            #foyda
            print(total_olgan_tavar_sum, 'aaaaaa')
            # print(total_olgan_tavar_kelish_sum, 'bbbbb')
            
            all_clint_tulagan_som += total_tulagan_som
            
            if qoldiq_qarz_sum > 0:
                all_clint_qarz_qoldiq_som += qoldiq_qarz_sum
                
            all_clint_daromad_som += mijozdan_daromad_sum
            
            # mijozdan_daromad_dollar = float(total_olgan_tavar_dollar) - float(total_olgan_tavar_kelish_dollar)
            #sum
            # all_clint_tulagan_dollar += total_tulagan_dollar
            #qarz sum
            # all_clint_qarz_qoldiq_dollar += qoldiq_qarz_dollar
            # all_clint_daromad_dollar += mijozdan_daromad_dollar
                
            dt = { 
                'fio': debror.fio,
                'total_tulagan_som': total_tulagan_som,
                # 'total_tulagan_dollar': total_tulagan_dollar,
                'qarz_sum': qarz_sum,
                # 'qarz_dollar': qarz_dollar,
                'total_olgan_tavar_sum': total_olgan_tavar_sum,
                # 'total_olgan_tavar_dollar': total_olgan_tavar_dollar,
                'qoldiq_qarz_sum': qoldiq_qarz_sum,
                # 'qoldiq_qarz_dollar': qoldiq_qarz_dollar,
                'mijozdan_daromad_sum': mijozdan_daromad_sum,
                # 'mijozdan_daromad_dollar': mijozdan_daromad_dollar,
                }
            ll.append(dt)

        context = {
            'malumotlar': ll,
            'all_clint_qarz_som': all_clint_qarz_som,
            # 'all_clint_qarz_dollar': all_clint_qarz_dollar,
            'all_clint_tulagan_som': all_clint_tulagan_som,
            # 'all_clint_tulagan_dollar': all_clint_tulagan_dollar,
            'all_clint_qarz_qoldiq_som': all_clint_qarz_qoldiq_som,
            # 'all_clint_qarz_qoldiq_dollar': all_clint_qarz_qoldiq_dollar,
            'all_clint_daromad_som': all_clint_daromad_som,
            # 'all_clint_daromad_dollar': all_clint_daromad_dollar,
        }
        context['dollar_kurs'] = Course.objects.last().som
        return render(request, 'get_ltv_data.html', context)
    
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'error'})
        

class Products(LoginRequiredMixin, TemplateView):
    template_name = 'product.html'

    def get_context_data(self, **kwargs):
        delivers = Deliver.objects.all()
        context = super().get_context_data(**kwargs)
        context['productfilials'] = ProductFilial.objects.all()
        context['productfilials_total_som'] = ProductFilial.objects.aggregate(Sum('som'))['som__sum']
        context['productfilials_total_dollar'] = ProductFilial.objects.aggregate(Sum('dollar'))['dollar__sum']
        context['productfilials_total_quantity'] = ProductFilial.objects.aggregate(Sum('quantity'))['quantity__sum']
        context['productfilials_total_min_count'] = ProductFilial.objects.aggregate(Sum('min_count'))['min_count__sum']
        product_filial = ProductFilial.objects.all()
        context['total_product_sum'] = sum(i.som * i.quantity for i in product_filial)
        context['product'] = 'active'
        context['product_t'] = 'true'
        context['delivers'] = delivers
        context['dollar_kurs'] = Course.objects.last().som

        return context


from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
from django.core.files.base import ContentFile

def create_barcode_image(product):
    barcode_length = len(product["barcode"])
    barcode_type = "ean13" if barcode_length == 12 else "code128"
    
    barcode_class = barcode.get_barcode_class(barcode_type)
    writer = ImageWriter()
    writer.set_options({
        "module_width": 0.6,
        "module_height": 40,
        "font_size": 5,
        "text_distance": 5,
        "dpi": 300,
    })
    barcode_instance = barcode_class(product["barcode"], writer=writer)
    
    buffer = BytesIO()
    barcode_instance.write(buffer)
    
    barcode_image = Image.open(buffer)
    barcode_image = barcode_image.resize((290, 120))
    
    width, height = 290, 210
    final_image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(final_image)
    
    font_path = os.path.join(settings.BASE_DIR, "static/Arial.ttf")
   
    try:
        font_medium = ImageFont.truetype(font_path, 15)
    except:
        font_medium = ImageFont.load_default()

    # Logotipni joylash
    logo = product['logo']
    logo = logo.resize((90, 90))  
    final_image.paste(logo, (110, -14), mask=logo if logo.mode == "RGBA" else None)

    draw.text((70, 50), product['name'], font=font_medium, fill="black")
    draw.text((40, 80), f"Artikul: {product['article']}", font=font_medium, fill="black")
    draw.text((195, 80), f"{product['price']} SUM", font=font_medium, fill="black")
 
    
    final_image.paste(barcode_image, (0, 100))

    rounded_mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(rounded_mask)
    mask_draw.rounded_rectangle([(0, 0), (width, height)], radius=30, fill=255)

    final_image = final_image.convert("RGBA")
    rounded_mask = rounded_mask.convert("L")
    final_image.putalpha(rounded_mask)

    output_buffer = BytesIO()
    final_image.save(output_buffer, format="PNG")

    return output_buffer.getvalue()

def create_barcode(request, id):
        product = ProductFilial.objects.get(id=id)
    # if product.barcode_image:
    #     return JsonResponse({'image':product.barcode_image.url}, safe=True)
    # else:
        logo_path = os.path.join(settings.BASE_DIR, "static", "bordo.png")  

        product_data = {
            'logo': Image.open(logo_path),
            "barcode": product.barcode,
            "name": product.name,
            "article": product.barcode,
            "price": product.som,
        }

        barcode_image_data = create_barcode_image(product_data)
        
        product.barcode_image.save(
            f"barcode_{product.barcode}.png",
            ContentFile(barcode_image_data),
            save=False
        )
        product.save()
        return JsonResponse({'image':product.barcode_image.url}, safe=True)



class ProductFilialView(LoginRequiredMixin, TemplateView):
    template_name = 'product_filial.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        deliver_id = self.request.GET.get('deliver')   
        debtor = self.request.GET.get('debtor', None)
        
        delivers = Deliver.objects.all()
        queryset = ProductFilial.objects.all()
        # total_recieve = 0
        # total_carts = 0

        if not start_date or not end_date:
            start_date = datetime.now().date().replace(day=1)
            end_date = datetime.now().date()
        
        if deliver_id:
            queryset = queryset.filter(deliver__id=deliver_id)
        
        # if debtor:
        #     queryset = queryset.filter(shop__debtor__id=debtor)
        data = []
        id_list = [i.id for i in queryset if i.return_carts(start_date, end_date, debtor) != 0]
        queryset = queryset.filter(id__in=id_list)
        for i in queryset:
            # for c in i.cart.all():
            # c_foyda = (i.sotish_som - c.price) * c.quantity

            dt = {
                'name': i.name,
                'preparer': i.preparer,
                'som': i.som,
                'quantity': i.quantity,
                'filial': i.filial,
                'barcode': i.barcode,
                'start_quantity': i.start_quantity,
                'jami_foyda': i.foyda(start_date, end_date, debtor),
                'recieve_quantity': i.return_recieves(start_date, end_date, deliver_id),
                'cart_quantity': i.return_carts(start_date, end_date, debtor)
            }
        # foyda += i(start_date, end_date)
        # jami_foyda += i.foyda(start_date, end_date) * i.return_carts(start_date, end_date)
            # dt['recieve_quantity'] = i.return_recieves(start_date, end_date)
            # dt['cart_quantity'] = i.return_carts(start_date, end_date)
            data.append(dt)
        data = reversed(sorted(data, key=lambda x: x['jami_foyda']))
        context['foyda_total'] = sum([i.foyda(start_date, end_date, debtor) for i in queryset])
        # context['jami_foyda_total'] = jami_foyda
        context['recieves_total'] = sum([i.return_recieves(start_date, end_date, deliver_id) for i in queryset])
        context['carts_total'] = sum([i.return_carts(start_date, end_date, debtor) for i in queryset])
        context['productfilials'] = data
        context['productfilials_total_som'] = queryset.aggregate(Sum('som'))['som__sum']
        context['productfilials_total_dollar'] = queryset.aggregate(Sum('dollar'))['dollar__sum']
        context['productfilials_total_quantity'] = queryset.aggregate(Sum('quantity'))['quantity__sum']
        context['productfilials_total_min_count'] = queryset.aggregate(Sum('min_count'))['min_count__sum']
        context['total_product_sum'] = sum(i.som * i.quantity for i in queryset)
        context['product'] = 'active'
        context['product_t'] = 'true'
        context['delivers'] = delivers
        context['dollar_kurs'] = Course.objects.last().som
        context['debtors'] = Debtor.objects.all().order_by('fio')

        context['filters'] = {
            'debtor': int(debtor) if debtor else 0,
            'start_date': start_date,
            'end_date': end_date,
        }
        # carts = Cart.objects.filter(date__date__gte=start_date, date__date__lte=end_date, shop__debtor__id=debtor).aggregate(Sum('quantity'))
        # print(carts)
        # for car in carts:
        #     print(car.quantity) 
        return context

from django.views import View

class DebtorAccountView(LoginRequiredMixin, View):
    
    def get(self, request):
        start_date = request.GET.get('start_date') if request.GET.get('start_date') else datetime.now().date().replace(day=1)
        end_date = request.GET.get('end_date') if request.GET.get('end_date') else datetime.now().date()
        debtors = Debtor.objects.all()
        data = []
        for debtor in debtors:
            shop = Shop.objects.filter(debtor=debtor, date__date__gte=start_date, date__date__lte=end_date)
            pay_history = PayHistory.objects.filter(debtor=debtor, date__date__gte=start_date, date__date__lte=end_date)
            shop_summa = sum([i.som for i in shop])
            product_count = sum([i.product_count for i in shop])
            payment_som = sum([i.som for i in pay_history])
            payment_dollar = sum([i.dollar for i in pay_history])
            dt = {
                'debtor': debtor,
                'shop_summa': shop_summa,
                'shop_count': shop.count(),
                'count': product_count,
                'payment_som': payment_som,
                'payment_dollar': payment_dollar
            }
            # if shop_summa or product_count or payment_dollar or payment_som != 0:
            data.append(dt)
        total_som = sum([i['payment_som'] for i in data])
        total_dollar = sum([i['payment_dollar'] for i in data])
        total_shop = sum([i['shop_summa'] for i in data])
        data = sorted(data, key=lambda instance: instance['shop_summa'])
        data.reverse()
        context = {
            'debtors': data,
            'start_date': start_date,
            'end_date': end_date,
            'total_som': total_som,
            'total_dollar': total_dollar,
            'total_shop': total_shop,
        }
        return render(request, 'debtor_account.html', context)


def deliver_filter(request): 
    delivers = Deliver.objects.all()
    productfilial = ProductFilial.objects.all()
    d_id = request.POST.get('d_id')
    deliver = Deliver.objects.get(id=d_id)

    som = 0
    quantity = 0
    total = 0
    dollar = 0

    products = deliver.products1.all()
    
    for product in products:
        som += product.som
        total += product.som * product.quantity
        quantity += product.quantity
        dollar += dollar

    # total = sum(i.som * i.quantity for i in product_filial)


    context = {
        'productfilials': products,
        'productfilials_total_som': som,
        'productfilials_total_quantity': quantity,
        'total_product_sum': total,
        'productfilials_total_dollar': dollar,
        'delivers': delivers,
        "deliver": deliver
    }
    context['dollar_kurs'] = Course.objects.last().som
    return render(request, 'product.html', context)



class Filials(LoginRequiredMixin, TemplateView):
    template_name = 'filial.html'

    def get_context_data(self, **kwargs):
        gte, lte = daily_data()
        # lte = timezone.now()
        # gte = lte - timedelta(days=1)
        som = 0
        dollar = 0
        
        filials = Filial.objects.extra(
            select={
                'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'pay_som': 'select sum(api_payhistory.som) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                    gte, lte),
                'pay_dollar': 'select sum(api_payhistory.dollar) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                    gte, lte)
            }
        )
        for f in filials:
            if f.naqd_som:
                som += f.naqd_som
                if f.plastik:
                    som += f.plastik
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                else:
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
            else:
                if f.plastik:
                    som += f.plastik
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                else:
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
            if f.naqd_dollar:
                dollar += f.naqd_dollar
                if f.nasiya_dollar:
                    dollar += f.nasiya_dollar
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
                else:
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
            else:
                if f.nasiya_dollar:
                    dollar += f.nasiya_dollar
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
                else:
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
        context = super().get_context_data(**kwargs)
        context['filial'] = 'active'
        context['filial_t'] = 'true'
        context['som'] = som
        context['dollar'] = dollar
        context['filials'] = filials
        context['dollar_kurs'] = Course.objects.last().som

        return context


class WareFakturas(LoginRequiredMixin, TemplateView):
    template_name = 'warefaktura.html'

    def get_context_data(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warefakturas'] = 'active'
        context['warefakturas_t'] = 'true'
        context['fakturas'] = Faktura.objects.filter(status=1)
        context['fakturaitems'] = FakturaItem.objects.all()
        context['dollar_kurs'] = Course.objects.last().som

        return context

class WareFakturaTarix(LoginRequiredMixin, TemplateView):
    template_name = 'warefakturatarix.html'

    def get_context_data(self, **kwargs):
        gte, lte = monthly()
        context = super().get_context_data(**kwargs)
        context['warefakturatarix'] = 'active'
        context['warefakturatarix_t'] = 'true'
        context['fakturas'] = Faktura.objects.filter(date__gte=gte, date__lte=lte)
        context['dollar_kurs'] = Course.objects.last().som
        return context


class Saler(LoginRequiredMixin, TemplateView):
    template_name = 'saler.html'

    def get_context_data(self, **kwargs):
        gte, lte = monthly()
        salers = UserProfile.objects.extra(
            select={
                'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
            }
        )
        som = 0
        dollar = 0
        for f in salers:
            if f.naqd_som:
                som += f.naqd_som
                if f.plastik:
                    som += f.plastik
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                else:
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
            else:
                if f.plastik:
                    som += f.plastik
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                else:
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
            if f.naqd_dollar:
                dollar += f.naqd_dollar
                if f.nasiya_dollar:
                    dollar += f.nasiya_dollar
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
                else:
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
            else:
                if f.nasiya_dollar:
                    dollar += f.nasiya_dollar
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
                else:
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
        context = super().get_context_data(**kwargs)
        context['saler'] = 'active'
        context['saler_t'] = 'true'
        context['salers'] = salers
        context['som'] = som
        context['dollar'] = dollar
        context['dollar_kurs'] = Course.objects.last().som
        return context


class Ombor(LoginRequiredMixin, TemplateView):
    template_name = 'ombor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['ombors'] = ProductFilial.objects.all()
        context['total_som'] = ProductFilial.objects.aggregate(Sum('som'))['som__sum']
        context['total_dollar'] = ProductFilial.objects.aggregate(Sum('dollar'))['dollar__sum']
        context['total_quantity'] = ProductFilial.objects.aggregate(Sum('quantity'))['quantity__sum']
        context['dollar_kurs'] = Course.objects.last().som

        return context


class OmborQabul(LoginRequiredMixin, TemplateView):
    template_name = 'omborqabul.html'

    def get_context_data(self, **kwargs):
        gte, lte = monthly()
        context = super().get_context_data(**kwargs)
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        deliver = self.request.GET.get('deliver')
        recieve = Recieve.objects.filter(status=2)
        if start_date and end_date:
            recieve = recieve.filter(date__date__gte=start_date, date__date__lte=end_date)
        else:
            recieve = recieve.filter(date__date__gte=datetime.now().date().replace(day=1))
        if deliver:
            recieve = recieve.filter(deliver_id=deliver)

        valyutas = Valyuta.objects.all()
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['wares'] = recieve
        context['dollar_kurs'] = Course.objects.last().som
        context['total_som'] = sum([i.som for i in context['wares']])
        context['total_som_sotish'] = sum([i.sum_sotish_som for i in context['wares']])
        context['total_quantity'] = sum([i.total_quantity if i.total_quantity else 0 for i in context['wares']])
        context['delivers'] = Deliver.objects.all()
        context['deliver'] = int(deliver) if deliver else 0
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['valyutas'] = valyutas

        total_valyutas = []
        for v in valyutas:
            dt = {
                "valyuta": v,
                "summa": sum([i.total_bring_price for i in recieve.filter(valyuta=v)]),
            }
            total_valyutas.append(dt)
        
        context['total_valyutas'] = total_valyutas

        # for r in Recieve.objects.filter(date__gte=gte, date__lte=lte):
        #     print(r.date)
        return context

from django.views.generic.detail import DetailView

class ArticleDetailView(LoginRequiredMixin, DetailView):
    model = Recieve
    template_name = 'omborqabul_detail.html'

    def get_context_data(self, **kwargs):
        
    #     context = super().get_context_data(**kwargs)
    #     context['dollar_kurs'] = Course.objects.last().som
    #     context['price_types'] = PriceType.objects.all()
    #     context['valyutas'] = Valyuta.objects.all()
        
    #     return context

        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['delivers'] = Deliver.objects.all().order_by('-id')
        context['recieves'] = Recieve.objects.filter(id=self.object.id).order_by('-id')
        context['recieveitems'] = RecieveItem.objects.filter(recieve__is_prexoded=False).order_by('-id')[:1000]
        context['dollar_kurs'] = Course.objects.last().som
        context['products'] = ProductFilial.objects.all()
        context['expanse_types'] = RecieveExpanseTypes.objects.all()
        context['external_users'] = ExternalIncomeUser.objects.filter(is_active=True)
        context['groups'] = Groups.objects.all()
        # context['delivers'] = Deliver.objects.all()
        context['filial'] = Filial.objects.filter(is_activate=True)
        context['price_types'] = PriceType.objects.filter(is_activate=True)
        context['valyutas'] = Valyuta.objects.filter()
        context['today'] = datetime.now()
        context['measurements'] = [{
            "id": i[0],
            "name": i[1],
        } for i in ProductFilial.measure]
        max_barcode = (
                ProductFilial.objects
                .annotate(barcode_int=Cast('barcode', IntegerField()))
                .aggregate(Max('barcode_int'))['barcode_int__max']
            )
        new_barcode = max_barcode+1 if max_barcode else 1

        context['new_barcode'] = new_barcode


        active_id = self.request.GET.get('active')
        if active_id and Recieve.objects.filter(id=active_id):
            context['active_one'] = Recieve.objects.get(id=active_id)
        return context

def omborqabul_recieve_detail(request, id):
    context = {
        'recieve':Recieve.objects.get(id=id),
        'item':RecieveItem.objects.filter(recieve_id=id),
    }
    return render(request, 'omborqabul_recieve_detail.html', context)

    
def edit_receive_count(request):
    id = request.POST.get('id')
    count = float(request.POST.get('count'))
    kelish_som = float(request.POST.get('som'))
    item = RecieveItem.objects.get(id=id)
    receive = Recieve.objects.get(id=item.recieve.id)
    deliver = receive.deliver
    # deliver.som -= item.som * item.quantity
    # deliver.dollar -= item.dollar * item.quantity
    receive.som -= item.som * item.quantity
    receive.dollar -= item.dollar * item.quantity
    receive.sum_sotish_som -= item.sotish_som * item.quantity
    receive.sum_sotish_dollar -= item.sotish_dollar * item.quantity
    # deliver.som += item.som * count
    # deliver.dollar += item.dollar * count
    receive.som += kelish_som * int(count)
    receive.dollar += item.dollar * int(count)
    receive.sum_sotish_som += item.sotish_som * int(count)
    receive.sum_sotish_dollar += item.sotish_dollar * int(count)
    payment = DeliverPayments.objects.filter(deliver=deliver).last()
    payments = payment.payments.filter(date__gte=receive.date).order_by('id')
    # payment1.received_total += int(instance.som) if instance.som else 0
    # payment1.received_total += (int(instance.dollar) if instance.dollar else 0) * Course.objects.last().som
    # son = item.quantity - count
    
    first = payments.first()
    # if kelish_som:
    first.received_total += item.quantity * item.som
    first.received_total -= count * kelish_som
    # if item.dollar:
    #     first.received_total += son * (item.dollar * Course.objects.last().som)
    first.save()
    # print(son, 'aaaaa')
    for i in payments:
        # if i.left != 0:
        i.left += item.quantity * item.som
        i.left -= count * kelish_som
        # i.left += (son) * (item.dollar * Course.objects.last().som)
        i.save()
    
    for i in RecieveItem.objects.filter(id__gt=item.id, product=item.product):
        i.old_quantity -= item.quantity - count
        i.save() 
    deliver.som = payments.last().left
    item.som = float(kelish_som)
    item.quantity = float(count)
    item.save()
    receive.save()
    deliver.save()
    return redirect(request.META['HTTP_REFERER'])



class DliverPayment(LoginRequiredMixin, TemplateView):
    template_name = 'deliverpayments.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = DeliverPayments.objects.all()
        context['dollar_kurs'] = Course.objects.last().som
        return context

    


class OmborMinus(LoginRequiredMixin, TemplateView):
    template_name = 'omborminus.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products = ProductFilial.objects.filter(quantity__lte=100).select_related('group')
        valyutas = list(Valyuta.objects.all())
        prices = ProductBringPrice.objects.filter(
            product__in=products,
            valyuta__in=valyutas
        ).select_related('product', 'valyuta').order_by('product_id', 'valyuta_id', '-id')

        last_price_dict = {}
        for price in prices:
            key = (price.product_id, price.valyuta_id)
            if key not in last_price_dict:  
                last_price_dict[key] = price.price

        data = []
        for product in products:
            dt = {
                'name': product.name,
                'preparer': product.preparer,
                'kurs': product.kurs,
                'quantity': product.quantity,
                'barcode': product.barcode,
                'group': product.group,
                'valyuta': []
            }
            for val in valyutas:
                summa = last_price_dict.get((product.id, val.id))
                dt['valyuta'].append({'summa': summa})
            data.append(dt)


        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['valyuta'] = valyutas
        context['ombors'] = data
        context['total_soni'] = ProductFilial.objects.aggregate(Sum('quantity'))['quantity__sum']
        context['dollar_kurs'] = Course.objects.last().som
        return context

class Fakturas(LoginRequiredMixin, TemplateView):
    template_name = 'faktura.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['fakturas'] = Faktura.objects.filter(status=1)
        context['fakturaitems'] = FakturaItem.objects.all().order_by('-id')[0:1000]
        context['dollar_kurs'] = Course.objects.last().som
        return context
    
from django.db.models import Max
class Recieves(LoginRequiredMixin, TemplateView):
    template_name = 'recieves.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['delivers'] = Deliver.objects.all().order_by('-id')
        context['recieves'] = Recieve.objects.filter(status__in=[0, 1], is_prexoded=False).order_by('-id')
        context['recieveitems'] = RecieveItem.objects.filter(recieve__is_prexoded=False).order_by('-id')[:1000]
        context['dollar_kurs'] = Course.objects.last().som
        context['products'] = ProductFilial.objects.all()
        context['expanse_types'] = RecieveExpanseTypes.objects.all()
        context['external_users'] = ExternalIncomeUser.objects.filter(is_active=True)
        context['groups'] = Groups.objects.all()
        # context['delivers'] = Deliver.objects.all()
        context['filial'] = Filial.objects.filter(is_activate=True)
        context['price_types'] = PriceType.objects.filter(is_activate=True)
        context['valyutas'] = Valyuta.objects.filter()
        context['today'] = datetime.now()
        context['measurements'] = [{
            "id": i[0],
            "name": i[1],
        } for i in ProductFilial.measure]
        max_barcode = (
                ProductFilial.objects
                .annotate(barcode_int=Cast('barcode', IntegerField()))
                .aggregate(Max('barcode_int'))['barcode_int__max']
            )
        new_barcode = max_barcode+1 if max_barcode else 1

        context['new_barcode'] = new_barcode


        active_id = self.request.GET.get('active')
        if active_id and Recieve.objects.filter(id=active_id):
            context['active_one'] = Recieve.objects.get(id=active_id)
        return context

def recieve_completion(request, id):
    re = Recieve.objects.get(id=id)
    re.status = 2
    re.deliver.som -= re.som
    re.deliver.dollar -= re.dollar
    re.deliver.save()
    re.save()
    DebtDeliver.objects.create(deliver=re.deliver, som=-re.som, dollar=-re.dollar, recieve=re)
    return redirect('omborqabul')

class FakturaTarix(LoginRequiredMixin, TemplateView):
    template_name = 'fakturatarix.html'

    def get_context_data(self, **kwargs):
        gte, lte = monthly()
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['fakturas'] = Faktura.objects.filter(date__gte=gte, date__lte=lte)
        context['dollar_kurs'] = Course.objects.last().som
        return context


def DataFak(request):
    data = json.loads(request.body)
    date1 = data['date1']
    date2 = data['date2']
    wares = Faktura.objects.filter(date__gte=date1, date__lte=date2)
    wr = []
    for w in wares:
        t = {
            'id': w.id,
            'summa': w.summa,
            'filial': w.filial.name,
            'difference': w.difference,
            'date': w.date.strftime("%d-%m-%y %I:%M")

        }
        wr.append(t)
    dt1 = {
        'wares': wr
    }
    return JsonResponse(dt1)


def GetFakturaItem(request):
    data = json.loads(request.body)
    id = data['id']
    items = FakturaItem.objects.filter(faktura_id=id)
    it = []
    for i in items:
        its = {
            'id': i.id,
            'product': i.product.name,
            'price': i.price,
            'quantity': i.quantity
        }
        it.append(its)
    dt1 = {
        'items': it
    }
    return JsonResponse(dt1)

class Table(TemplateView):
    template_name = 'table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = 'active'
        context['table_t'] = 'true'
        context['dollar_kurs'] = Course.objects.last().som
        return context

class DataTable(TemplateView):
    template_name = 'datatable.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datatable'] = 'active'
        context['datatable_t'] = 'true'
        context['dollar_kurs'] = Course.objects.last().som
        return context


class Hodim(LoginRequiredMixin, TemplateView):
    template_name = 'hodim.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hodim'] = 'active'
        context['hodim_t'] = 'true'
        context['salers'] = UserProfile.objects.filter(~Q(staff=1),active=True)
        context['filials'] = Filial.objects.all()
        context['dollar_kurs'] = Course.objects.last().som
        return context

def delete_hodim(request, id):
    print(dir(request.user),"shef keldi")
    if request.user.userprofile.staff == 1:
        bad_hodim = UserProfile.objects.get(id=id)
        bad_hodim.active=False
        bad_hodim.save()
    else:
        pass
    return redirect('hodim')


class Debtors(LoginRequiredMixin, TemplateView):
    template_name = 'debtor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        debtor = Debtor.objects.select_related('agent','teritory').all()
        paginator_debtor = Paginator(debtor, 50)
        page_number = self.request.GET.get('page')
        page_debtor = paginator_debtor.get_page(page_number)
        dollar_kurs = Course.objects.last().som

        context['debtor'] = 'active'
        context['debtor_t'] = 'true'
        context['debtors'] = page_debtor
        context['debtor_type'] = DebtorType.objects.all()
        context['teritory'] = Teritory.objects.all()
        context['agent'] = MobilUser.objects.all()
        context['valyuta'] = Valyuta.objects.all()
        context['dollar_kurs'] = dollar_kurs
        context['cashes'] = KassaNew.objects.filter(is_active=True)
        return context

def debtor_add(request):
    type = request.POST.get('type')
    teritory = request.POST.get('teritory')
    agent = request.POST.get('agent')
    image = request.FILES.get('image')
    fio = request.POST.get('fio')
    phone1 = request.POST.get('phone1')
    phone2 = request.POST.get('phone2')
    Debtor.objects.create(
        type_id=type,
        teritory_id=teritory,
        agent_id=agent,
        image=image,
        fio=fio,
        phone1=phone1,
        phone2=phone2,
    )
    return redirect(request.META['HTTP_REFERER'])

def debtor_edit(request, id):
    type = request.POST.get('type')
    teritory = request.POST.get('teritory')
    agent = request.POST.get('agent')
    image = request.FILES.get('image')
    fio = request.POST.get('fio')
    phone1 = request.POST.get('phone1')
    phone2 = request.POST.get('phone2')
    deb = Debtor.objects.get(id=id)
    deb.type_id=type
    deb.teritory_id=teritory
    deb.agent_id=agent
    if image is not None:
        deb.image=image
    deb.fio=fio
    deb.phone1=phone1
    deb.phone2=phone2
    deb.save()
    return redirect(request.META['HTTP_REFERER'])

def debtor_pay(request, id):
    debt = Debtor.objects.get(id=id)
    summa = request.POST.get('summa')
    valyuta = request.POST.get('valyuta')
    comment = request.POST.get('comment')
    PayHistory.objects.create(debtor_id=id, valyuta_id=valyuta, summa=summa, comment=comment)
    debt.refresh_debt()
    return redirect(request.META['HTTP_REFERER'])

def debtor_give(request, id):
    debt = Debtor.objects.get(id=id)
    summa = request.POST.get('summa')
    valyuta = request.POST.get('valyuta')
    comment = request.POST.get('comment')
    PayHistory.objects.create(debtor_id=id, valyuta_id=valyuta, summa=summa, comment=comment, type_pay=2)
    debt.refresh_debt()
    return redirect(request.META['HTTP_REFERER'])

def debtor_detail(request, id):
    valyuta = Valyuta.objects.all()
    debt_shot = Wallet.objects.filter(customer_id=id)
    debtor = Debtor.objects.get(id=id)
    today = datetime.now().date()

    start_date = request.GET.get('start_date', today.replace(day=1))
    end_date = request.GET.get('end_date', today)

    filters = {
        'start_date': str(start_date),
        'end_date': str(end_date),
    }
   
    pay = PayHistory.objects.filter(debtor_id=id, date__date__range=(start_date, end_date))
    shop = Shop.objects.filter(debtor_id=id, date__date__range=(start_date, end_date))
    bonus = Bonus.objects.filter(debtor_id=id, date__date__range=(start_date, end_date))

    infos = sorted(chain(pay, shop, bonus), key=lambda instance: instance.date)
    data = []
    for i in infos:
        dt = {
            'id': i.id,
            'date': i.date,
            'comment': i.comment,
            'valyuta': i.valyuta,
            'debt_new': i.debt_new,
        }
        if i._meta.model_name == 'payhistory':
            if i.type_pay == 1:
                dt['type_payment'] = 'Pul olindi'
                dt['pay_summa'] = i.summa
            else:
                dt['type_payment'] = 'Pul Berildi'
                dt['give_summa'] = i.summa
            
        elif i._meta.model_name == 'shop':
            dt['type_payment'] = 'Maxsulot sotildi'
            dt['pay_summa'] = i.baskets_total_price
        
        elif i._meta.model_name == 'bonus':
            dt['type_payment'] = 'Bonus berildi'
            if i.summa <= 0:
                dt['pay_summa'] = i.summa
            else:
                dt['give_summa'] = i.summa

        data.append(dt)
    summa_total_for_valyuta = []
    for val in valyuta:
        pay_summa = pay.filter(valyuta=val, type_pay=1).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all']
        pay_shop_summa = shop.filter(valyuta=val).annotate(summa=Sum(F('cart__price') * F('cart__quantity'), output_field=IntegerField())).aggregate(all=Coalesce(Sum('summa'), 0, output_field=IntegerField()))['all']
        dt_sum_valyuta = {
            'valyuta':val.id,
            'pay_pay_summa':pay_summa + pay_shop_summa,
            'pay_give_summa':pay.filter(valyuta=val, type_pay=2).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all'],
        }
        summa_total_for_valyuta.append(dt_sum_valyuta)
    
    context = {
        'valyuta':valyuta,
        'summa_total_for_valyuta':summa_total_for_valyuta,
        'debt_shot':debt_shot,
        'pay':pay,
        'data':data,
        'filters':filters,
        'debtor':debtor,
    }
    return render(request, 'debtor_detail.html', context)



def deliver_detail(request, id):
    valyuta = Valyuta.objects.all()
    debt_shot = Wallet.objects.filter(deliver_id=id)
    deliver = Deliver.objects.get(id=id)
    today = datetime.now().date()

    start_date = request.GET.get('start_date', today.replace(day=1))
    end_date = request.GET.get('end_date', today)

    filters = {
        'start_date': str(start_date),
        'end_date': str(end_date),
    }
   
    pay = PayHistory.objects.filter(deliver_id=id, date__date__range=(start_date, end_date))
    recieve = Recieve.objects.filter(deliver_id=id, date__date__range=(start_date, end_date))
    bonus = Bonus.objects.filter(deliver_id=id, date__date__range=(start_date, end_date))


    infos = sorted(chain(pay, recieve, bonus), key=lambda instance: instance.date)
    data = []
    for i in infos:
        dt = {
            'id': i.id,
            'date': i.date,
            'comment': i.comment,
            'valyuta': i.valyuta,
            'debt_new': i.debt_new,
        }
        if i._meta.model_name == 'payhistory':
            if i.type_pay == 1:
                dt['type_payment'] = 'Pul olindi'
                dt['pay_summa'] = i.summa
            else:
                dt['type_payment'] = 'Pul Berildi'
                dt['give_summa'] = i.summa
            
        elif i._meta.model_name == 'recieve':
            dt['type_payment'] = 'Maxsulot qabul'
            dt['pay_summa'] = i.summa_total
        
        elif i._meta.model_name == 'bonus':
            dt['type_payment'] = 'Bonus berildi'
            if i.summa <= 0:
                dt['pay_summa'] = i.summa
            else:
                dt['give_summa'] = i.summa

        data.append(dt)

    summa_total_for_valyuta = []
    for val in valyuta:
        pay_summa = pay.filter(valyuta=val, type_pay=1).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all']
        pay_recieve_summa = sum([i.summa_total for i in recieve.filter(valyuta=val)])
        dt_sum_valyuta = {
            'valyuta':val.id,
            'pay_pay_summa':pay_summa + pay_recieve_summa,
            'pay_give_summa':pay.filter(valyuta=val, type_pay=2).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all'],
        }
        summa_total_for_valyuta.append(dt_sum_valyuta)
    
    context = {
        'valyuta':valyuta,
        'summa_total_for_valyuta':summa_total_for_valyuta,
        'debt_shot':debt_shot,
        'pay':pay,
        'data':data,
        'filters':filters,
        'deliver':deliver,
    }
    return render(request, 'deliver_detail.html', context)



def income_user_detail(request):
    pass
    id = request.GET.get('d')
    valyuta = Valyuta.objects.all()
    debt_shot = Wallet.objects.filter(partner_id=id)
    partner = ExternalIncomeUser.objects.get(id=id)
    today = datetime.now().date()

    start_date = request.GET.get('start_date', today.replace(day=1))
    end_date = request.GET.get('end_date', today)

    filters = {
        'start_date': str(start_date),
        'end_date': str(end_date),
    }
   
    pay = PayHistory.objects.filter(external_income_user_id=id, date__date__range=(start_date, end_date))
    bonus = Bonus.objects.filter(partner_id=id, date__date__range=(start_date, end_date))


    infos = sorted(chain(pay, bonus), key=lambda instance: instance.date)
    data = []
    for i in infos:
        dt = {
            'id': i.id,
            'date': i.date,
            'comment': i.comment,
            'valyuta': i.valyuta,
            'debt_new': i.debt_new,
        }
        if i._meta.model_name == 'payhistory':
            if i.type_pay == 1:
                dt['type_payment'] = 'Pul olindi'
                dt['pay_summa'] = i.summa
            else:
                dt['type_payment'] = 'Pul Berildi'
                dt['give_summa'] = i.summa
        
        elif i._meta.model_name == 'bonus':
            dt['type_payment'] = 'Bonus berildi'
            if i.summa <= 0:
                dt['pay_summa'] = i.summa
            else:
                dt['give_summa'] = i.summa

        data.append(dt)

    summa_total_for_valyuta = []
    for val in valyuta:
        pay_summa = pay.filter(valyuta=val, type_pay=1).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all']
        dt_sum_valyuta = {
            'valyuta':val.id,
            'pay_pay_summa':pay_summa,
            'pay_give_summa':pay.filter(valyuta=val, type_pay=2).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all'],
        }
        summa_total_for_valyuta.append(dt_sum_valyuta)
    
    context = {
        'valyuta':valyuta,
        'summa_total_for_valyuta':summa_total_for_valyuta,
        'debt_shot':debt_shot,
        'pay':pay,
        'data':data,
        'filters':filters,
        'partner':partner,
    }
    return render(request, 'partner_detail.html', context)



class Delivers(LoginRequiredMixin, TemplateView):
    template_name = 'deliver.html'



    def get_context_data(self, **kwargs):
        delivers = Deliver.objects.all()
        dollar_kurs = Course.objects.last().som
        pass
        # for dl in Deliver.objects.all().order_by('-id'):
        #     gte, lte = monthly()
        #     d_id = dl.id
        #     # pays = DeliverPayHistory.objects.filter(date__gte=gte, date__lte=lte, deliver_id=d_id)
        #     # debts = DebtDeliver.objects.filter(date__gte=gte, date__lte=lte, deliver_id=d_id)
        #     dollar_kurs = Course.objects.last().som
        #     # psom = 0
        #     # pdollar = 0
        #     # dsom = 0
        #     # ddollar = 0
        #     # for p in pays:
        #     #     psom += p.som
        #     #     psom += p.dollar * dollar_kurs
        #     #     # pdollar += p.dollar
        #     # for d in debts:
        #     #     dsom += d.som
        #     #     # ddollar += d.dollar
        #     debtor = {
        #         'dsom1': dl.som,
        #         'ddollor1': dl.dollar,
        #         'name': f'{dl.name}',
        #         'phone1': f'{dl.phone1}',
        #         'phone2': f'{dl.phone2}' if dl.phone2 else "Yo'q",
        #         'id': f'{dl.id}',
        #     }

        #     delivers.append(debtor)
        valutas = Valyuta.objects.all()
        context = super().get_context_data(**kwargs)
        context['deliver'] = 'active'
        context['deliver_t'] = 'true'
        context['delivers'] = delivers
        context['total_som'] = Deliver.objects.aggregate(Sum('som'))['som__sum']
        context['total_dollar'] = Deliver.objects.aggregate(Sum('dollar'))['dollar__sum']
        context['dollar_kurs'] = dollar_kurs
        context['valyuta'] = valutas

        context['total_haq'] = [
                {'summa': Wallet.objects.filter(deliver__in=delivers, valyuta=val, summa__gt=0).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all']}
                for val in valutas
            ]
        context['total_qarz'] = [
                {'summa': Wallet.objects.filter(deliver__in=delivers, valyuta=val, summa__lt=0).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all']}
                for val in valutas
            ]

        context['cashes'] = KassaNew.objects.filter(is_active=True)
        # 'valyuta':Valyuta.objects.all(),
        # 'cashes':KassaNew.objects.filter(is_active=True),
        return context

class FakturaYoqlama(LoginRequiredMixin, TemplateView):
    template_name = 'fakturayoqlama.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kamomads'] = Kamomad.objects.all()
        context['dollar_kurs'] = Course.objects.last().som
        return context

class Profile(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_t'] = 'true'
        context['dollar_kurs'] = Course.objects.last().som
        # context['user'] = UserProfile.objects.get(username)

        return context

class ProfileSetting(TemplateView):
    template_name = 'profile-setting.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_t'] = 'true'
        context['dollar_kurs'] = Course.objects.last().som
        return context

class SweetAlert(TemplateView):
    template_name = 'sweet-alert.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sweet_alert'] = 'active'
        context['sweet_alert_t'] = 'true'
        context['dollar_kurs'] = Course.objects.last().som
        return context

class Date(TemplateView):
    template_name = 'date.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = 'active'
        context['date_t'] = 'true'
        context['dollar_kurs'] = Course.objects.last().som
        return context

class Widget(TemplateView):
    template_name = 'widget.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['widget'] = 'active'
        context['widget_t'] = 'true'
        context['dollar_kurs'] = Course.objects.last().som
        return context

from django.contrib.auth.hashers import check_password


# def Login(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         try:
#             use = User.objects.filter(username=username).last()
#             if use and use.check_password(password):
#                 if use.userprofile.staff == 4:
#                     login(request, use)
#                     return redirect('omborqabul')
#                 else:
#                     profile = UserProfile.objects.filter(user=use).last()
#                     if profile:
#                         if profile.is_bussines:
#                             return redirect('home')
#                         elif profile.is_maxsulot_boshkaruvi:
#                             return redirect('product')
#                         elif profile.is_maxsulot_tahriri:
#                             return redirect('product_editing_page')
#                         elif profile.is_taminotchi_qaytuv:
#                             return redirect('deliver_return')
#                         elif profile.is_bugungi_sotuvlar:
#                             return redirect('today_sales')
#                         elif profile.is_maxsutlo_tahlili:
#                             return redirect('product_filial')
#                         elif profile.is_analiz_xarajatlar:
#                             return redirect('analysis_costs')
#                         elif profile.is_ot_tarix:
#                             return redirect('tovar_prixod_tarix')
#                         elif profile.is_ot_prixod:
#                             return redirect('tovar_prixod')
#                         elif profile.is_hisobdan_chiqish:
#                             return redirect('write_off')
#                         elif profile.is_hisobdan_tarix:
#                             return redirect('write_off_tarix')
#                         elif profile.is_xodim_kunlik:
#                             return redirect('one_day_price')
#                         elif profile.is_xodim_oylik:
#                             return redirect('employee')
#                         elif profile.is_xodim_mobile:
#                             return redirect('mobile_order')
#                         elif profile.is_xodim_call_center:
#                             return redirect('call_center_payment')
#                         elif profile.is_fin_hisoboti:
#                             return redirect('fin_report')
#                         elif profile.is_buyurtmalar:
#                             return redirect('shops')
#                         elif profile.is_filial_boshkaruvi:
#                             return redirect('filial')
#                         elif profile.is_kadrlar:
#                             return redirect('hodim')
#                     else:
#                         login(request, use)
#                         return redirect('home')
#             else:
#                 messages.error(request, 'Login yoki Parol notogri kiritildi!')
#                 return redirect('login')
#         except:
#             messages.error(request, 'Login yoki Parol notogri kiritildi!')
#             return redirect('login')
#     else:
#         return render(request, 'login.html')


def Login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.filter(username=username).last()
        if user and user.check_password(password):
            profile = getattr(user, 'userprofile', None)

            if user.userprofile.staff == 4:
                login(request, user)
                return redirect('omborqabul')

            redirect_map = {
                'is_bussines': 'home',
                'is_maxsulot_boshkaruvi': 'product',
                'is_maxsulot_tahriri': 'product_editing_page',
                'is_taminotchi_qaytuv': 'deliver_return',
                'is_bugungi_sotuvlar': 'today_sales',
                'is_maxsutlo_tahlili': 'product_filial',
                'is_analiz_xarajatlar': 'analysis_costs',
                'is_ot_tarix': 'tovar_prixod_tarix',
                'is_ot_prixod': 'tovar_prixod',
                'is_hisobdan_chiqish': 'write_off',
                'is_hisobdan_tarix': 'write_off_tarix',
                'is_xodim_kunlik': 'one_day_price',
                'is_xodim_oylik': 'employee',
                'is_xodim_mobile': 'mobile_order',
                'is_xodim_call_center': 'call_center_payment',
                'is_fin_hisoboti': 'fin_report',
                'is_buyurtmalar': 'shops',
                'is_filial_boshkaruvi': 'filial',
                'is_kadrlar': 'hodim',
                'is_mijozlar_qarzdorligi': 'debtor',
                'is_mijozlar_tahlili': 'debtor_account',
                'is_yetkazib_beruvchilar': 'deliver',
                'is_ombor_boshkaruvi_ombor': 'ombor',
                'is_ombor_boshkaruvi_qabul': 'omborqabul',
                'is_ombor_boshkaruvi_ombordan_analiz': 'omborminus',
                'is_reyting_maxsulotlar': 'top_products',
                'is_reyting_mijozlar': 'top_debtors',
                'is_reyting_yetkazib_beruvchilar': 'top_delivers',
                'is_kassa': 'kassa',
                'is_savdo': 'create_order',
                'is_nds': 'nds_page',
                'is_b2b_savdo': 'b2b_shop',
                'is_bugungi_amaliyotlar':'todays_practices',
                'is_kassa_tasdiklanmagan': 'kassa_is_approved',
                'is_kassa_tarixi': 'desktop_kassa',
                'is_qabul': 'recieve',
                'is_reviziya':'reviziya',
                'is_reviziya_tarixi':'revision_complate',
                'is_turli_shaxs':'externalincomeuser',
                'is_taminotchi_qaytuv_tarix':'deliver_return_tarix',
                'is_filial_kassalar':'filial_kassalar',
                'is_measurement_type':'measurement_type_list',
                'is_price_type':'price_type',
                'is_filial_list':'filial_list',
                'is_valyuta':'valyuta_list',
                'is_kassa_merge':'kassa_merge',
                'is_kassa_new':'kassa_new_list',
                'is_money_circulation':'money_circulation',
                
            }

            if profile:
                for attr, route in redirect_map.items():
                    if getattr(profile, attr, False):
                        login(request, user)
                        return redirect(route)

            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Login yoki Parol notogri kiritildi!')
            return redirect('login')
    return render(request, 'login.html')

# def Login(request):
#     if request.method == "POST":
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         # if user is not None:
#         #     login(request, user)
#         #     return redirect('home')
#         # else:
#         #     messages.error(request, 'Login yoki Parol notogri kiritildi!')
#         #     return redirect('login')
#         if use.userprofile.staff == 4:
# #                 login(request, use)
# #                 return redirect('omborqabul')
# #             else:
# #                 login(request, use)
# #                 return redirect('home')
#     else:
#         return render(request, 'login.html')


def Logout(request):
    logout(request)
    messages.success(request, "Tizimdan chiqish muvaffaqiyatli yakunlandi!")
    return redirect('login')


def kassa(request):
    bugun = datetime.now()
    hodimlar = HodimModel.objects.all()
    kassa_var = Kassa.objects.first()
    expenses = FilialExpense.objects.all()
    branches = Filial.objects.all()

    hodimlar_qarz = []
    shu_oylik_chiqimlar = Chiqim.objects.filter(is_approved=True).order_by('-id')
    shu_oylik_kirimlar = Kirim.objects.filter(is_approved=True).order_by('-id')
    # if request.method == 'POST':
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    deliver = [int(i) for i in request.GET.getlist('deliver')  if i != '']
    debtor = [int(i) for i in request.GET.getlist('debtor')  if i != '']
    chiqim_turi = request.GET.get('chiqim_turi')
    category = [int(i) for i in request.GET.getlist('category')  if i != '']
    subcategory = [int(i) for i in request.GET.getlist('subcategory')  if i != '']
    if start_date and end_date:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qachon__gte=start_date, qachon__lte=end_date).order_by('-qachon')
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qachon__gte=start_date, qachon__lte=end_date).order_by('-qachon')
        expenses = expenses.filter(created_at__range=(start_date, end_date)).order_by('-created_at')
    else:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qachon__year=bugun.year, qachon__month=bugun.month).order_by('-qachon')
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qachon__year=bugun.year, qachon__month=bugun.month).order_by('-qachon')
        expenses = expenses.filter(created_at__year=bugun.year, created_at__month=bugun.month).order_by('-created_at')

    if deliver:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(deliver_id__in=deliver)
    
    if debtor:
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(payhistory__debtor_id__in=debtor)

    if chiqim_turi:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qayerga_id=chiqim_turi)
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qayerga_id=chiqim_turi)
    
    if category:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(subcategory__category_id__in=category)

    if subcategory:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(subcategory_id__in=subcategory)

    # if expanse_category:
    #     expenses = expenses.filter(category_id=expanse_category)

    categories = ChiqimCategory.objects.all()
    subcategories = ChiqimSubCategory.objects.all()
    valutas = Valyuta.objects.all()
    
    # chiqim_total_som = shu_oylik_chiqimlar.aggregate(Sum('qancha_som'))['qancha_som__sum']
    # chiqim_total_dollar = shu_oylik_chiqimlar.aggregate(Sum('qancha_dol'))['qancha_dol__sum']
    # chiqim_hisob_raqam_total = shu_oylik_chiqimlar.aggregate(Sum('qancha_hisob_raqamdan'))['qancha_hisob_raqamdan__sum']
    # chiqim_plastik = shu_oylik_chiqimlar.aggregate(Sum('plastik'))['plastik__sum']
    
    # kirim_total_som = shu_oylik_kirimlar.aggregate(Sum('qancha_som'))['qancha_som__sum']
    # kirim_total_dollar = shu_oylik_kirimlar.aggregate(Sum('qancha_dol'))['qancha_dol__sum']
    # kirim_hisob_raqam_total = shu_oylik_kirimlar.aggregate(Sum('qancha_hisob_raqamdan'))['qancha_hisob_raqamdan__sum']
    # kirim_plastik = shu_oylik_kirimlar.aggregate(Sum('plastik'))['plastik__sum']

    for hodim in hodimlar:
        qarz_som = 0
        qarz_dol = 0
        for q in hodim.hodimqarz_set.filter(tolandi=False):
            qarz_som += q.qancha_som
            qarz_dol += q.qancha_dol

        dt = {
            'id': hodim.id,
            'ism_familya':hodim.toliq_ism_ol(),
            'filial':hodim.filial.name,
            'qarz_som':qarz_som,
            'qarz_dol':qarz_dol,   
        }

        hodimlar_qarz.append(dt)
    
    total_expenses = expenses.aggregate(foo=Coalesce(
        Sum('total_sum'),
        0, output_field=FloatField()
    ))['foo']

    hodimlar_royxat = [
        hodim
        for hodim in hodimlar
        if not OylikTolov.objects.filter(
            hodim_id=hodim.id, sana__year=bugun.year, sana__month=bugun.month
        ).exists()
    ]
    kassa = KassaMerge.objects.filter(is_active=True)
    filial = Filial.objects.all()
    data = []
    for i in KassaNew.objects.all():
        dt = {
            'name':i.name,
            'valyuta':[
                {'name':val.name , 'summa': kassa.filter(valyuta=val, kassa=i).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all'] }
                for val in Valyuta.objects.all()
            ],
        }
        data.append(dt)
    
    kirim_totals = [{
        "summa": shu_oylik_kirimlar.filter(valyuta=v).aggregate(sum=Sum('summa'))['sum']
    } for v in valutas]

    chiqim_totals = [{
        "summa": shu_oylik_chiqimlar.filter(valyuta=v).aggregate(sum=Sum('summa'))['sum']
    } for v in valutas]

    round_chart = []

    for i in KassaNew.objects.all():
        dt = {
            'name':i.name,
            'summa_som': kassa.filter(kassa=i, valyuta__is_som=True).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all'] ,
            'summa_dol': kassa.filter(kassa=i, valyuta__is_dollar=True).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all'] ,
        }
        round_chart.append(dt)


    chart_month = []

    year = datetime.date.fromisoformat(start_date).year if start_date else bugun.year

    months = {
        '1': 'Yan', '2': 'Fev', '3': 'Mart', '4': 'Apr',
        '5': 'May', '6': 'Iyun', '7': 'Iyul', '8': 'Avg',
        '9': 'Sen', '10': 'Okt', '11': 'Noy', '12': 'Dek',
    }

    chart_chiqim = Chiqim.objects.filter(qachon__year=year) \
        .values('qachon__month') \
        .annotate(summa=Coalesce(Sum(F('summa') / F('currency')), 0, output_field=IntegerField()))
    
    chart_shop = Shop.objects.filter(date__year=year) \
        .values('date__month') \
        .annotate(total=Sum((F('cart__quantity')*F('cart__price')) / F('kurs')))
    
    chart_chiqim_dict = {item['qachon__month']: item for item in chart_chiqim}
    chart_shop_dict = {item['date__month']: item for item in chart_shop}


    for i in range(1, 13):
        chiqim_sum = chart_chiqim_dict.get(i, {}).get('summa') or 0
        shop_sum = chart_shop_dict.get(i, {}).get('total') or 0
        cht_month = {
            'month': months.get(str(i), ''),
            'chiqim_summa': chiqim_sum,
            'shop_summa': shop_sum,
        }
        chart_month.append(cht_month)

    content = {
        'chart_month':chart_month,
        'round_chart':round_chart,
        'kassa_active':'active',
        'kassa_true':'true',
        'kirim_totals':kirim_totals,
        'chiqim_totals':chiqim_totals,
        'hodimlar':hodimlar_royxat,
        'barcha_hodimlar':hodimlar,
        'shu_oylik_chiqimlar':shu_oylik_chiqimlar,
        'shu_oylik_kirimlar':shu_oylik_kirimlar,
        # "chiqim_turlari":chiqim_turlari,
        'categories':categories,
        'subcategories':subcategories,
        'hodimlar_qarz':hodimlar_qarz,
        'kassa':kassa_var,
        'valutas': valutas,
        # 'chiqim_total_som': chiqim_total_som,
        # 'chiqim_total_dollar': chiqim_total_dollar,
        # 'chiqim_hisob_raqam_total': chiqim_hisob_raqam_total,
        # 'kirim_total_som': kirim_total_som,
        # 'kirim_total_dollar': kirim_total_dollar,
        # 'kirim_hisob_raqam_total': kirim_hisob_raqam_total,
        # 'chiqim_plastik': chiqim_plastik,
        # 'kirim_plastik': kirim_plastik,
        'filial': "active",
        'filial_t': "true",
        'filials': branches,
        # 'current_filial': current_filial,
        'total_expenses': total_expenses,
        'expenses': expenses,
        'chiqim_turi': ChiqimTuri.objects.all(),
        'expanse_category': FilialExpenseCategory.objects.all(),
        'delivers': Deliver.objects.all(),
        'debtors': Debtor.objects.all(),
        'valuta': Valyuta.objects.all(),
        'cashes': KassaNew.objects.all(),
        'money_circulation': MoneyCirculation.objects.filter(is_delete=True),
        'bugun_year':bugun.year,
        'data':data,
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'deliver': deliver,
            # 'chiqim_turi': int(chiqim_turi) if chiqim_turi else 0,
            'category': category,
            'subcategory': subcategory,
            'debtor': debtor
        }
    }
    content['dollar_kurs'] = Course.objects.last().som
    return render(request, 'kassa.html', content)

    

def hodimga_qarz(request):
    if request.method == "POST":
        kassa_var = Kassa.objects.first()
        uslub = request.POST['uslub']

        if uslub == 'yangi':

            hodim_id = request.POST['hodim_id']
            qancha_som = request.POST.get('qancha_som')
            qancha_dol = request.POST.get('qancha_dol')
            izox = request.POST.get('izox')
            
            if qancha_som.isdigit() or qancha_dol.isdigit():
                
                if not qancha_dol.isdigit():
                    qancha_dol = 0
                    
                if not qancha_som.isdigit():
                    qancha_som = 0
                  
                if int(qancha_som) > 0 or int(qancha_dol) > 0:
                    qarz = HodimQarz.objects.create(hodim_id=hodim_id, izox=izox)

                    if qancha_som:
                        qarz.qancha_som += int(qancha_som)
                        kassa_var.som -= int(qancha_som)

                    if qancha_dol:
                        qarz.qancha_dol += int(qancha_dol)
                        kassa_var.dollar -= int(qancha_dol)

                    qarz.save()
                    kassa_var.save()
                    
                    messages.info(request, "Qarz berildi!")
                    messages.info(request, f"hodim: {HodimModel.objects.get(id=hodim_id).toliq_ism_ol()}.")
                    messages.info(request, f"So'm: {qancha_som}")
                    messages.info(request, f"$: {qancha_dol}")
                
                else:
                    messages.info(request, "0 miqdorda qarz bermoqchimisiz! 🤔" )
                
            
            else:
                messages.info(request, "😡 Biror pul miqdorini kiritib keyin bosing!")
            
        
        else:

            qarz_id = request.POST['qarz_id']
            hodim_id = request.POST['hodim_id']
            qancha_som = request.POST.get('qancha_som')
            qancha_dol = request.POST.get('qancha_dol')
            izox = request.POST['izox']

            qarz = HodimQarz.objects.get(id=qarz_id)

            if qancha_som:
                qarz.qaytargani_som += int(qancha_som)
                kassa_var.som += int(qancha_som)
            
            if qancha_dol:
                qarz.qaytargani_dol += int(qancha_dol)
                kassa_var.dollar += int(qancha_dol)

            qarz.qaytargandagi_izox = izox
            qarz.save()
            kassa_var.save()
            qarz.qarzni_tekshir()

            messages.info(request, "To'lov qabul qilindi")

            return redirect(f'/hodim-qarzlari/?hodim_id={hodim_id}')

        return redirect('/kassa/')


def hodim_qarzlari(request):
    
    hodim_id = request.GET['hodim_id']
    hodim = HodimModel.objects.get(id=hodim_id)
    qarzlari = hodim.hodimqarz_set.filter(tolandi=False)

    

    return render(request, 'hodim_qarzlari.html', {'hodim':hodim, 'qarzlari':qarzlari, 'dollar_kurs': Course.objects.last().som})


# def chiqim_qilish(request):
    
#     """ Kassadan chiqim qiladi """

#     if request.method == 'POST':
        
#         chiqim_turi = request.POST.get('chiqim_turi')
#         qancha_som = request.POST.get('qancha_som')
#         qancha_dol = request.POST.get('qancha_dol')
#         plastik = request.POST.get('qancha_plastik')
        
#         qancha_hisob_raqamdan = request.POST.get('qancha_hisob_raqamdan')
#         izox = request.POST['izox']

#         kassa_var = Kassa.objects.first()


#         chiqim = Chiqim.objects.create(qayerga_id=chiqim_turi, izox=izox)
#         if qancha_som and kassa_var.som >= int(qancha_som):
#             chiqim.kassa_som_eski = kassa_var.som
#             chiqim.qancha_som = qancha_som
#             kassa_var.som -= int(qancha_som)
#             chiqim.kassa_som_yangi = kassa_var.som
        
#         if plastik:
#             chiqim.kassa_plastik_eski = kassa_var.plastik
#             chiqim.plastik = plastik
#             kassa_var.plastik -= int(plastik)
#             chiqim.kassa_plastik_yangi = kassa_var.plastik

#         if qancha_dol and kassa_var.dollar >= int(qancha_dol):
#             chiqim.kassa_dol_eski = kassa_var.dollar
#             chiqim.qancha_dol = qancha_dol
#             kassa_var.dollar -= int(qancha_dol)
#             chiqim.kassa_dol_yangi = kassa_var.dollar
            
#         if qancha_hisob_raqamdan and kassa_var.hisob_raqam >= int(qancha_hisob_raqamdan):
#             chiqim.kassa_hisob_raqam_eski = kassa_var.hisob_raqam
#             chiqim.qancha_hisob_raqamdan = qancha_hisob_raqamdan
#             kassa_var.hisob_raqam -= int(qancha_hisob_raqamdan)
#             chiqim.kassa_hisob_raqam_yangi = kassa_var.hisob_raqam
            
#         chiqim.save()
#         kassa_var.save()

#         return redirect('/kassa/')



def chiqim_qilish(request):

    """ Kassadan chiqim qiladi """

    if request.method == 'POST':
        pass
        subcategory = request.POST.get('subcategory')
        kurs = request.POST.get('kurs')
        valuta_id = request.POST.get('valuta')
        kassa_id = request.POST.get('kassa')
        summa = request.POST.get('summa')
        izox = request.POST['izox']
        debtor = request.POST.get('debtor')
        deliver = request.POST.get('deliver')
        partner = request.POST.get('partner')
        qaysi_oy = int(request.POST.get('qaysi_oy'))
        qaysi_yil = int(request.POST.get('qaysi_yil'))
        qaysi = date(qaysi_yil, qaysi_oy, 1)
        money_circulation = request.POST.get('money_circulation')
        
        valuta = Valyuta.objects.get(id=valuta_id)
        cash = KassaNew.objects.get(id=kassa_id)

        kassa = KassaMerge.objects.filter(kassa=cash, valyuta=valuta).last() or KassaMerge.objects.create(kassa=cash, valyuta=valuta)

        chiqim = Chiqim.objects.create(izox=izox, subcategory_id=subcategory,
                                        kassa=kassa, valyuta=valuta, currency=kurs, 
                                        summa=summa, money_circulation_id=money_circulation, qaysi=qaysi,
                                        )

        reja = RejaChiqim.objects.create(kassa=cash, valyuta=valuta,
                                          plan_total=summa, kurs=kurs, is_confirmed=True,
                                          money_circulation_id=money_circulation, qaysi=qaysi,)
        chiqim.reja_chiqim=reja
        kassa.summa -= float(summa)

        chiqim.kassa_new = kassa.summa

        if debtor:
            pay = PayHistory.objects.create(debtor_id=debtor, comment=izox, kassa=kassa, valyuta=valuta, currency=kurs, summa=summa, type_pay=2)
            chiqim.payhistory=pay
            deb = Debtor.objects.get(id=debtor)
            deb.refresh_debt()
            text = 'Pul olindi \n'
            text += f'\t\t\t {chiqim.summa}-{chiqim.valyuta.name}'
            chat_id = deb.tg_id
            send_message(chat_id, text)
        
        if deliver:
            pay = PayHistory.objects.create(deliver_id=deliver, comment=izox, kassa=kassa, valyuta=valuta, currency=kurs, summa=summa, type_pay=2)
            chiqim.payhistory=pay
            Deliver.objects.get(id=deliver).refresh_debt()

        if partner:
            pay = PayHistory.objects.create(external_income_user_id=partner, comment=izox, kassa=kassa, valyuta=valuta, currency=kurs, summa=summa, type_pay=2)
            chiqim.payhistory=pay
            ExternalIncomeUser.objects.get(id=partner).refresh_debt()

        kassa.save()
        chiqim.save()

        return redirect(request.META['HTTP_REFERER'])


def chiqim_qilish_edit(request):
    """ Chiqimni tahrirlash va kassa qoldiqlarini yangilash """
    chiqim_id = request.POST.get('chiqim_id')
    chiqim = Chiqim.objects.get(id=chiqim_id)

    eski_summa = float(chiqim.summa)
    eski_kurs = float(chiqim.currency)

    if request.method == 'POST':
        yangi_summa = float(request.POST.get('summa'))
        yangi_kurs = float(request.POST.get('kurs'))
        yangi_izoh = request.POST.get('izox')
        yangi_subcat = request.POST.get('subcategory')

        # Chiqimni yangilash
        chiqim.summa = yangi_summa
        chiqim.currency = yangi_kurs
        chiqim.izox = yangi_izoh
        chiqim.subcategory_id = yangi_subcat

        farq = eski_summa - yangi_summa  # chiqim kamaytirilgan bo‘lsa, qoldiq oshadi

        kassa = chiqim.kassa
        kassa.summa += farq
        kassa.save()

        chiqimlar = Chiqim.objects.filter(kassa=kassa, id__gte=chiqim.id).order_by('id')
        qoldiq = kassa.summa

        chiqim.save()

        for ch in chiqimlar:
            if ch.id == chiqim.id:
                qoldiq = qoldiq
            else:
                qoldiq -= float(ch.summa)

            ch.kassa_new = qoldiq
            ch.save()

        return redirect(request.META['HTTP_REFERER'])




# def chiqim_qilish_edit(request):
    
#     """ Kassadan chiqni tahrirlaydi """

#     if request.method == 'POST':
#         chiqim_id = request.POST.get('chiqim_id')
#         chiqim_turi = request.POST.get('chiqim_turi')
#         qancha_som = request.POST.get('qancha_som', 0)
#         qancha_dol = request.POST.get('qancha_dol', 0)
#         qancha_hisob_raqamdan = request.POST.get('qancha_hisob_raqamdan', 0)
#         izox = request.POST['izox']
#         plastik = request.POST.get('qancha_plastik', 0)
#         kassa_var = Kassa.objects.first()
#         chiqim = Chiqim.objects.get(id=chiqim_id)
    
#         deliver = chiqim.deliver
        

#         deliver_payments = DeliverPayments.objects.filter(deliver=deliver).last()
#         if deliver_payments:
#             payments = deliver_payments.payments
#         else:
#             payments = None

#         deliverpayment = chiqim.deliverpayment
#         # if chiqim_turi:
#         #     chiqim.qayerga.id = chiqim_turi
#         if izox is not None and izox != '':
#             chiqim.izox = izox

#         # qayerga_id=chiqim_turi, izox=izox
#         if qancha_som and kassa_var.som + chiqim.qancha_som - float(qancha_som) >= 0:
#             left_som = chiqim.qancha_som - int(qancha_som)
#             if payments:
#                 deliverpayment.left -= float(left_som)
#                 for i in payments.filter(id__gt=deliverpayment.id):
#                     i.left -= float(left_som)
#                     deliver.som = i.left
#                     i.save()
#                     deliver.save()
            
#             chiqim.kassa_som_eski = kassa_var.som + float(chiqim.qancha_som)
#             chiqim.qancha_som_eski = chiqim.qancha_som

#             deliverpayment = chiqim.deliverpayment
#             if deliverpayment:
#                 deliverpayment.gave_total = int(qancha_som)
#                 deliverpayment.save()
#             # if deliver:
#             #     deliver.som += chiqim.qancha_som
#             #     deliver.som -= int(qancha_som)

#             kassa_var.som += chiqim.qancha_som

#             chiqim.qancha_som = qancha_som

#             kassa_var.som -= int(qancha_som)

#             chiqim.kassa_som_yangi = kassa_var.som

#         if qancha_dol and kassa_var.dollar + chiqim.qancha_dol - float(qancha_dol) >= 0:
#             left_dollar = chiqim.qancha_dol - int(qancha_dol) * int(Course.objects.last().som)
#             if payments:
#                 deliverpayment.left -= float(left_dollar) * Course.objects.last().som
#                 for i in payments.filter(id__gt=deliverpayment.id):
#                     i.left -= float(left_dollar) * Course.objects.last().som
#                     deliver.som = i.left
#                     i.save()
#                     deliver.save()

#             if deliverpayment:
#                 deliverpayment.gave_total = int(qancha_dol) * Course.objects.last().som
#                 deliverpayment.save()
#             # if deliver:
#             #     deliver.som += chiqim.qancha_dol * Course.objects.last().som
#             #     deliver.som -= int(qancha_dol) * Course.objects.last().som
#             chiqim.kassa_dol_eski = kassa_var.dollar + float(chiqim.qancha_dol)
#             chiqim.qancha_dol_eski = chiqim.qancha_dol
#             kassa_var.dollar += chiqim.qancha_dol
#             chiqim.qancha_dol = qancha_dol
#             kassa_var.dollar -= int(qancha_dol)
#             chiqim.kassa_dol_yangi = kassa_var.dollar

            
#         # if plastik:
#         if plastik and kassa_var.plastik + chiqim.plastik - float(plastik) >= 0:
#             # if deliverpayment:
#             #     deliverpayment.gave_total = int(plastik)
#             #     deliverpayment.save()
#             # if deliver:
#             #     deliver.som += chiqim.plastik
#             #     deliver.som -= int(plastik)

#             left_plastik = chiqim.plastik - float(plastik)
#             if payments:
#                 deliverpayment.left -= float(left_plastik)
#                 for i in payments.filter(id__gt=deliverpayment.id):
#                     i.left -= float(left_plastik)
#                     deliver.som = i.left
#                     i.save()
#                     deliver.save()

#             deliverpayment = chiqim.deliverpayment
#             if deliverpayment:
#                 deliverpayment.gave_total = float(plastik)
#                 deliverpayment.save()
#             # if deliver:
#             #     deliver.som += chiqim.plastik
#             #     deliver.som -= float(plastik)
                    
#             chiqim.kassa_plastik_eski = kassa_var.plastik + float(chiqim.plastik)
#             chiqim.plastik_eski = chiqim.plastik
#             kassa_var.plastik += chiqim.plastik
#             chiqim.plastik = plastik
#             kassa_var.plastik -= int(plastik)
#             chiqim.kassa_plastik_yangi = kassa_var.plastik

            
#         # if qancha_hisob_raqamdan and kassa_var.hisob_raqam >= int(qancha_hisob_raqamdan):
#         if qancha_hisob_raqamdan and kassa_var.hisob_raqam + chiqim.qancha_hisob_raqamdan - float(qancha_hisob_raqamdan) >= 0:
#             # if deliverpayment:
#             #     deliverpayment.gave_total = int(qancha_hisob_raqamdan)
#             #     deliverpayment.save()

#             # if deliver:
#             #     deliver.som += chiqim.qancha_hisob_raqamdan
#             #     deliver.som -= int(qancha_hisob_raqamdan)

#             left_qancha_hisob_raqamdan = chiqim.qancha_hisob_raqamdan - float(qancha_hisob_raqamdan)
#             if payments:
#                 deliverpayment.left -= float(left_qancha_hisob_raqamdan)
#                 for i in payments.filter(id__gt=deliverpayment.id):
#                     i.left -= float(left_qancha_hisob_raqamdan)
#                     deliver.som = i.left
#                     i.save()
#                     deliver.save()

#             deliverpayment = chiqim.deliverpayment
#             if deliverpayment:
#                 deliverpayment.gave_total = float(qancha_hisob_raqamdan)
#                 deliverpayment.save()
#             # if deliver:
#             #     deliver.som += chiqim.qancha_hisob_raqamdan
#             #     deliver.som -= float(qancha_hisob_raqamdan)
            
            
#             chiqim.kassa_hisob_raqam_eski = kassa_var.hisob_raqam + float(chiqim.qancha_hisob_raqamdan)
#             chiqim.qancha_hisob_raqamdan_eski = chiqim.qancha_hisob_raqamdan
#             kassa_var.hisob_raqam += chiqim.qancha_hisob_raqamdan
#             chiqim.qancha_hisob_raqamdan = qancha_hisob_raqamdan
#             kassa_var.hisob_raqam -= int(qancha_hisob_raqamdan)
#             chiqim.kassa_hisob_raqam_yangi = kassa_var.hisob_raqam
        
#         # print(deliverpayment.left, 'jjjjj')
#         chiqim.save()
#         kassa_var.save()
#         if deliver:
#             deliver.save()

#         return redirect('/kassa/')
    
#kirim

from tg_bot.bot import send_message, send_kirim_message
from django.contrib.humanize.templatetags.humanize import intcomma

def kirim_qilish(request):

    """ Kassadan kirim qiladi """

    if request.method == 'POST':
        pass
        debtor = request.POST.get('debtor')
        # plastik = request.POST.get('plastik')
        kurs = request.POST.get('kurs')
        debtor = request.POST.get('debtor')
        deliver = request.POST.get('deliver')
        partner = request.POST.get('partner')
        valuta_id = request.POST.get('valuta')
        kassa_id = request.POST.get('kassa')
        summa = request.POST.get('summa')
        izox = request.POST['izox']

        valuta = Valyuta.objects.get(id=valuta_id)
        cash = KassaNew.objects.get(id=kassa_id)

        kassa = KassaMerge.objects.filter(kassa=cash, valyuta=valuta).last() or KassaMerge.objects.create(kassa=cash, valyuta=valuta)

        kirim = Kirim.objects.create(izox=izox, kassa=kassa, valyuta=valuta, currency=kurs, summa=summa)
        
        kassa.summa += float(summa)

        kirim.kassa_new = kassa.summa
        if debtor:
            pay = PayHistory.objects.create(debtor_id=debtor, comment=izox, kassa=kassa, valyuta=valuta, currency=kurs, summa=summa, type_pay=1)
            kirim.payhistory=pay
            deb = Debtor.objects.get(id=debtor)
            deb.refresh_debt()
            text = 'Pul olindi \n'
            text += f'💴 {intcomma(kirim.summa)} {kirim.valyuta.name}'
            text += f'💸 {intcomma(kirim.currency) }'
            text += f"📅 {kirim.qachon.strftime('%Y-%m-%d %H:%M')}"
            if kirim.izox:
                text += f'💬 {kirim.izox}'
            chat_id = deb.tg_id
            send_kirim_message(chat_id, text, kirim.id)
        
        if deliver:
            pay = PayHistory.objects.create(deliver_id=deliver, comment=izox, kassa=kassa, valyuta=valuta, currency=kurs, summa=summa, type_pay=1)
            kirim.payhistory=pay
            Deliver.objects.get(id=deliver).refresh_debt()

        if partner:
            pay = PayHistory.objects.create(external_income_user_id=partner, comment=izox, kassa=kassa, valyuta=valuta, currency=kurs, summa=summa, type_pay=1)
            kirim.payhistory=pay
            ExternalIncomeUser.objects.get(id=partner).refresh_debt()


        kassa.save()
        kirim.save()
       

        return redirect(request.META['HTTP_REFERER'])


def kirim_qilish_edit(request):
    """ Kirimni tahrirlash va kassa qoldiqlarini yangilash """
    kirim_id = request.POST.get('kirim_id')
    kirim = Kirim.objects.get(id=kirim_id)
    eski_summa = float(kirim.summa)
    eski_kurs = float(kirim.currency)

    if request.method == 'POST':
        yangi_summa = float(request.POST.get('summa'))
        yangi_kurs = float(request.POST.get('kurs'))
        yangi_izoh = request.POST.get('izox')

        # Obyektni yangilash
        kirim.summa = yangi_summa
        kirim.currency = yangi_kurs
        kirim.izox = yangi_izoh

        if kirim.payhistory:
            kirim.payhistory.summa = yangi_summa
            kirim.payhistory.currency = yangi_kurs
            kirim.payhistory.comment = yangi_izoh
            kirim.payhistory.save()

        # Kassa farqini hisoblaymiz
        farq = yangi_summa - eski_summa

        # KassaMerge dagi qiymatni yangilaymiz
        kassa = kirim.kassa
        kassa.summa += farq

        # Hozirgi kirim va keyingi kirimlar uchun kassa_new qiymatlarini yangilaymiz
        kirimlar = Kirim.objects.filter(kassa=kassa, id__gte=kirim.id).order_by('id')
        qoldiq = kassa.summa
        kassa.save()
        kirim.save()

        for k in kirimlar:
            if k.id == kirim.id:
                qoldiq = qoldiq  # aynan bu obyekt uchun qoldiq shundoq bo'ladi
            else:
                qoldiq += float(k.summa)

            k.kassa_new = qoldiq
            k.save()

        # Agar qarzdor bo‘lsa, uning qarzini yangilaymiz
        if kirim.payhistory and kirim.payhistory.debtor:
            kirim.payhistory.debtor.refresh_debt()
        return redirect(request.META['HTTP_REFERER'])

    

# def kirim_qilish_edit(request):

#     """ Kassadan kirimni tahrirlaydi """

#     if request.method == 'POST':
#         kirim_id = request.POST.get('kirim_id')
#         plastik = request.POST.get('plastik')
#         qancha_som = request.POST.get('qancha_som')
#         qancha_dol = request.POST.get('qancha_dol')
#         qancha_hisob_raqamdan = request.POST.get('qancha_hisob_raqamdan')
#         izox = request.POST['izox']
#         kassa_var = Kassa.objects.first()


#         chiqim = Kirim.objects.get(id=kirim_id)
#         if izox:
#             chiqim.izox = izox
#         if qancha_som:
#             chiqim.qancha_som_eski = chiqim.qancha_som
#             kassa_var.som -= chiqim.qancha_som
#             chiqim.qancha_som = qancha_som
#             kassa_var.som += int(qancha_som)
#             chiqim.kassa_som_yangi = kassa_var.som
#             chiqim.kassa_som_eski = chiqim.kassa_som_yangi - int(qancha_som)
            
#         if plastik:
#             chiqim.plastik_eski = chiqim.plastik
#             kassa_var.plastik -= chiqim.plastik
#             chiqim.plastik = plastik
#             kassa_var.plastik += int(plastik)
#             chiqim.kassa_plastik_yangi = kassa_var.plastik
#             chiqim.kassa_plastik_eski = chiqim.kassa_plastik_yangi - int(plastik)

#         if qancha_dol:
#             chiqim.qancha_dol_eski = chiqim.qancha_dol
#             kassa_var.dollar -= chiqim.qancha_dol
#             chiqim.qancha_dol = qancha_dol
#             kassa_var.dollar += int(qancha_dol)
#             chiqim.kassa_dol_yangi = kassa_var.dollar
#             chiqim.kassa_dol_eski = chiqim.kassa_dol_yangi - int(qancha_dol)
            
#         if qancha_hisob_raqamdan:
#             chiqim.qancha_hisob_raqamdan_eski = chiqim.qancha_hisob_raqamdan
#             kassa_var.hisob_raqam -= chiqim.qancha_hisob_raqamdan
#             chiqim.qancha_hisob_raqamdan = qancha_hisob_raqamdan
#             kassa_var.hisob_raqam += int(qancha_hisob_raqamdan)
#             chiqim.kassa_hisob_raqam_yangi = kassa_var.hisob_raqam
#             chiqim.kassa_hisob_raqam_eski = chiqim.kassa_hisob_raqam_yangi - int(qancha_hisob_raqamdan)
#         chiqim.save()
#         kassa_var.save()

#         return redirect('/kassa/')


def oylik_tolash(request):
    if request.method == "POST":
        
        hodim_id = request.POST['hodim_id']
        kassa_var = Kassa.objects.first()
        hodim = HodimModel.objects.get(id=hodim_id)

        OylikTolov.objects.create(hodim_id=hodim_id, pul=hodim.oylik)

        kassa_var.som -= hodim.oylik
        kassa_var.save()

        return redirect('/kassa/')



#998997707572 len = 12
def checkPhone(phone):
    try:
        int(phone)
        return (True, phone) if len(phone) >= 12 else (False, None)
    except:
        return False, None
#for fio and qarz som
def sms_text_replace(sms_text, customer):
    try:
        format_som = '{:,}'.format(int(customer.som))
        sms_texts = str(sms_text).format(name = customer.fio, som = format_som)
    except Exception as e:
        print(e)
    
    return sms_texts
#for fio
def sms_text_replaces(sms_text, customer):
    try:
        sms_texts = str(sms_text).format(name = customer.fio)
    except Exception as e:
        print(e)
    
    return sms_texts


# vaqt = datetime.now().date()
# debtors = Debtor.objects.filter(debt_return__day=vaqt.day, debt_return__month=vaqt.month, debt_return__year=vaqt.year)
# print(debtors)
# print('aaa')

# from django.conf import settings
#sms sender  if date today  
def schedular_sms_send():
    try:
        success_send_count = 0
        error_send_count = 0
        text = settings.DEADLINE_SMS
        vaqt = datetime.now().date()
        debtors = Debtor.objects.filter(debt_return__day=vaqt.day, debt_return__month=vaqt.month, debt_return__year=vaqt.year)

        text = "Bugun to'lov qilishi kerak bolgan mijozlar: \n\n"

        for debtor in debtors:
            if debtor.som > 0 or debtor.dollar > 0:
                text += f'Ismi: {debtor.fio}\n'
                text += f'Telefon: {debtor.phone1}\n'
                text += f'Dollar: {debtor.dollar}\n'
                text += f"So'm: {debtor.som}\n"
                text += f"\n"
        
        token = settings.BOT_TOKEN
        chat_id = settings.TELEGRAM_GROUP_ID

        url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text
        results = requests.get(url_req)
        print(results)
        # for debtor in debtors:
        #     sms_text = sms_text_replaces(text, debtor)
        #     can, phone = checkPhone(debtor.phone1)
        #     if can:
        #         sendSmsOneContact(debtor.phone1, sms_text)
        #         success_send_count += 1
        #     else:
        #         error_send_count += 1

        # token = Company.bot_token
    # chat_id = Company.group_chat_id
    except Exception as e:
        print(e) 


# schedular_sms_send()

# schedular_sms_send()
        
        
# old deptors 
def schedular_sms_send_olds():
    try:
        success_send_count = 0
        error_send_count = 0
        text = settings.OLD_DEADLINE_SMS
        vaqt = datetime.now().date()
        
        debtors = Debtor.objects.filter(debt_return__day__lt=vaqt.day, debt_return__month__lte=vaqt.month, debt_return__year__lte=vaqt.year)

        for debtor in debtors:
            sms_text = sms_text_replaces(text, debtor)
            can, phone = checkPhone(debtor.phone1)
            if can:
                result = sendSmsOneContact(debtor.phone1, sms_text)
                success_send_count += 1
            else:
                error_send_count += 1
    except Exception as e:
        print(e)   

from datetime import timedelta  
# send 3days agos deptors 
def schedular_sms_send_alert():
    try:
        success_send_count = 0
        error_send_count = 0
        text = settings.THREE_DAY_AGO_SMS
        # 3kun oldingi kunlar
        thire_day_future = datetime.today() + timedelta(days=3)
        thire_day_future_date = thire_day_future.date()
        debtors = Debtor.objects.filter(debt_return__day=thire_day_future_date.day, debt_return__month=thire_day_future_date.month, debt_return__year=thire_day_future_date.year, som__gt = 0 , dollar__gt = 0)

        for debtor in debtors:
            sms_text = sms_text_replace(text, debtor)
            can, phone = checkPhone(debtor.phone1)
            if can:
                sendSmsOneContact(debtor.phone1, sms_text)
                success_send_count += 1
            else:
                error_send_count += 1
    except Exception as e:
        print(e)



def add_dollar_kursi(request):
    som = float(request.POST.get('som'))
    print(som)
    if Course.objects.all().exists():
        course = Course.objects.last()
        course.som = som
        course.save()
    else:
        course = Course.objects.create(som=som) 
    return redirect(request.META['HTTP_REFERER'])


def add_payment_comment(request):
    id = request.POST.get('payment_id')
    comment = request.POST.get('comment')
    
    payment = DeliverPaymentsAll.objects.get(id=int(id))
    payment.check_comment = comment
    payment.save()
    
    return redirect(request.META['HTTP_REFERER'])




def income_status_change(request):
    income_id = int(request.GET.get('id'))
    comment = request.GET.get('comment')
    income = CashboxReceive.objects.get(id=income_id)
    income.status = request.GET.get('status')
    # income.director_description = comment
    if income.status =='accepted':
        kassa = Kassa.objects.last()
        kirim = Kirim.objects.create(izox=income.description)
        if income.currency == "so'm":
            kirim.qancha_som = income.total_sum
            kirim.kassa_som_eski = kassa.som
            kassa.som += income.total_sum
            kirim.kassa_som_yangi = kassa.som

        elif income.currency == "dollar":
            kirim.qancha_dol = income.total_sum
            kirim.kassa_dol_eski = kassa.dollar
            kassa.dollar += income.total_sum
            kirim.kassa_dol_yangi = kassa.dollar

        elif income.currency == "carta":
            kirim.plastik = income.total_sum
            kirim.kassa_plastik_eski = kassa.plastik
            kassa.plastik += income.total_sum
            kirim.kassa_plastik_yangi = kassa.plastik

        elif income.currency == "utkazma":
            kirim.qancha_hisob_raqamdan = income.total_sum
            kirim.kassa_hisob_raqam_eski = kassa.hisob_raqam
            kassa.hisob_raqam += income.total_sum
            kirim.kassa_hisob_raqam_yangi = kassa.hisob_raqam
        
        kirim.save()
        kassa.save()
    

    income.save()
    filial = int(request.GET.get('filial'))
    return redirect(f'/filialinfo/{filial}/')



def null_products(request):
    for i in ProductFilial.objects.all():
        i.quantity = 0
        i.save()
    return redirect(request.META['HTTP_REFERER'])


def allFilter(request):
    date = request.GET.get('date')
    day = datetime.now().date()

    if date:
        day = date


    product_daily=ProductFilialDaily.objects.filter(date=day)
    debtor_daily=DebtorDaily.objects.filter(date=day)
    deliver_daily=DeliverDaily.objects.filter(date=day)
    kass_som=KassaDaily.objects.filter(date=day)

    totals = {
        "product_daily": product_daily.aggregate(sum=Sum('rest'))['sum'],
        "debtor_daily": debtor_daily.aggregate(sum=Sum('rest'))['sum'],
        # "debtor_daily_qarz": debtor_daily.filter(rest__gt=0).aggregate(sum=Sum('rest'))['sum'],
        # "debtor_daily_haq": debtor_daily.filter(rest__lt=0).aggregate(sum=Sum('rest'))['sum'],

        "deliver_daily": deliver_daily.aggregate(sum=Sum('rest'))['sum'],
        # "deliver_daily_qarz": deliver_daily.filter(rest__gt=0).aggregate(sum=Sum('rest'))['sum'],
        # "deliver_daily_haq": deliver_daily.filter(rest__lt=0).aggregate(sum=Sum('rest'))['sum'],
        # "kass_som": kass_som.aggregate,
    }

    context = {
        'date': date,
        'totals': totals,
        'product_daily':product_daily,
        'debtor_daily':debtor_daily,
        'deliver_daily':deliver_daily,
        'kassa_daily':kass_som,
    }

    return render(request, 'all_filter.html', context)


class ShopView(LoginRequiredMixin, View):

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        shop = Shop.objects.all()
        print(start_date, end_date)
        if start_date and end_date:
            shop = shop.filter(date__date__gte=start_date, date__date__lte=end_date)
        else:
            shop = shop.filter(date__date__gte=datetime.now().date().replace(day=1))
        context = {
            'shop': shop,
            'shop_total': sum([i.som for i in shop]),
            'shop_count': sum([i.product_count for i in shop]),
            'start_date': start_date,
            'end_date': end_date
        }
        return render(request, 'shop.html', context)


def shop_detail(request, id):
    shop = Shop.objects.get(id=id)
    context = {
        'shop': shop
    }
    return render(request, 'shop_detail.html', context)


import calendar

# def get_dates_in_month(year, month):
#     num_days = calendar.monthrange(year, month)[1]  # Get the number of days in the month
#     dates = [f"{year}-{month:02d}-{day:02d}" for day in range(1, num_days + 1)]
#     return dates

# # Example usage:
# year = 2024
# month = 4
# dates = get_dates_in_month(year, month)

# employes = UserProfile.objects.filter(staff=3,  daily_wage=False)
# for date in dates:
#     print(date)
    # for i in employes:
    #     i.refresh_total(date)


# today = datetime.today()
# for car in Cart.objects.filter(shop__saler__staff=3, date__month=today.month).distinct():
#     print(car)
#     car.save()

def employee(request):
    month = request.GET.get('month')
    employe = request.GET.get('employe')
    today = datetime.today()
    employes = UserProfile.objects.filter(staff=3,  daily_wage=False)

    if employe:
        employes = employes.filter(id=employe)
    if month:
        year, month = month.split('-')
        today = date(int(year), int(month), 1)

        
    days_of_month = int(calendar.monthrange(int(today.year), int(today.month))[1])
    dates = [x for x in range(1, days_of_month+1)]
    query = FlexPrice.objects.filter(sana__month=today.month)
    data = []
    for i in employes:
        total =  query.filter(sana__year=today.year, is_status=False, sana__month=today.month, user_profile=i).count() * i.price_and                
        all_summa = query.filter(is_status=True, sana__year=today.year, sana__month=today.month, total__gt=i.after)
        total_oylik = []
        total_sum = []
        for suma in all_summa.filter(user_profile= i).distinct():
            narx = int(suma.total)-int(i.after)
            total_sum.append(narx)
        for oylik in Chiqim.objects.filter(user_profile=i, qachon__month=today.month):
            pul = oylik.qancha_som
            total_oylik.append(pul)
        dt = {
                "employee": i,
                "days": [],
                "flex": sum(total_sum) * i.flex_price,
                "monthly": sum(total_sum) * i.flex_price + i.fix_price - total,
                # 'total_oylik':sum(total_sum) * i.flex_price + i.fix_price - total - sum(total_oylik),
                'tolangan_pul':sum(total_oylik),
            }
        dt['total_oylik'] = dt['monthly'] - dt['tolangan_pul']
        for day in dates:
            obj, created = query.get_or_create(sana=today.replace(day=day), user_profile=i)
            dt['days'].append(obj)
        data.append(dt)
    context = {
        'date': dates,
        'last_data': data[0] if data else {},
        'chiqim_turlari': ChiqimTuri.objects.all(),
        'employee_price': query,    
        'data':data,
        
    }
    return render(request, 'employee.html', context)




def call_center_payment(request):
    month = request.GET.get('month')
    employe = request.GET.get('employe')
    today = datetime.today()
    employes = UserProfile.objects.filter(staff=6,  daily_wage=False)

    if employe:
        employes = employes.filter(id=employe)
    if month:
        year, month = month.split('-')
        today = date(int(year), int(month), 1)

        
    days_of_month = int(calendar.monthrange(int(today.year), int(today.month))[1])
    dates = [x for x in range(1, days_of_month+1)]
    query = FlexPrice.objects.filter(sana__month=today.month)
    data = []
    for i in employes:
        total =  query.filter(sana__year=today.year, is_status=False, sana__month=today.month, user_profile=i).count() * i.price_and                
        all_summa = query.filter(is_status=True, sana__year=today.year, sana__month=today.month, total__gt=i.after)
        total_oylik = []
        total_sum = []
        for suma in all_summa.filter(user_profile= i).distinct():
            narx = int(suma.total)-int(i.after)
            total_sum.append(narx)
        for oylik in Chiqim.objects.filter(user_profile=i, qachon__month=today.month):
            pul = oylik.qancha_som
            total_oylik.append(pul)
        dt = {
                "employee": i,
                "days": [],
                "count": sum(total_sum),
                "flex": sum(total_sum) * i.flex_price,
                "monthly": sum(total_sum) * i.flex_price + i.fix_price - total,
                # 'total_oylik':sum(total_sum) * i.flex_price + i.fix_price - total - sum(total_oylik),
                'tolangan_pul':sum(total_oylik),
            }
        dt['total_oylik'] = dt['monthly'] - dt['tolangan_pul']
        for day in dates:
            obj, created = query.get_or_create(sana=today.replace(day=day), user_profile=i)
            dt['days'].append(obj)
        data.append(dt)
    
    totals = {
        "days": []
    }
    for day in dates:
        total = query.filter(sana=today.replace(day=day), user_profile__in=employes).aggregate(sum=Sum('total'))['sum']
        totals['days'].append({
            'total': total if total else 0
        })
    context = {
        'date': dates,
        'totals': totals,
        'last_data': data[0] if data else {},
        'chiqim_turlari': ChiqimTuri.objects.all(),
        'employee_price': query,    
        'data':data,
        'chiqim_turlari':ChiqimTuri.objects.filter(for_employee=True),
        
    }
    return render(request, 'employee.html', context)


def detail_call_center_count(request, employee_id):
    employee = UserProfile.objects.get(id=employee_id)
    year, month = request.GET.get('month', datetime.now().strftime('%Y-%m')).split('-')
    carts = Cart.objects.filter(shop__date__month=month, shop__date__year=year, shop__call_center=employee.username).distinct()

    totals = {
        "quantity": carts.aggregate(sum=Sum('quantity'))['sum'],
        "price": carts.aggregate(sum=Sum('price'))['sum'],
        "total": carts.aggregate(sum=Sum(F('quantity') * F('price')))['sum'],
        "for_call_center": sum([i.for_call_center for i in carts]),
    }
    context = {
        'carts': carts,
        'employee': employee,
        'totals': totals,
    }
    return render(request, 'detail_counts.html', context)

def flex_status_change(request, id):
    sana = request.POST.get('sana')
    one = FlexPrice.objects.get(user_profile__id=id, sana=sana)
    one.sana=sana
    one.is_status = False
    one.save()
    return redirect("employee")    


def payment_employee(request, id):
       if request.method == 'POST':
        
        chiqim_turi = int(request.POST.get('chiqim_turi'))
        qancha_som = request.POST.get('qancha_som')
        qancha_dol = request.POST.get('qancha_dol')
        plastik = request.POST.get('qancha_plastik')
        
        qancha_hisob_raqamdan = request.POST.get('qancha_hisob_raqamdan')
        izox = request.POST['izox']

        kassa_var = Kassa.objects.first()

        
        user = UserProfile.objects.get(id=id)
        # chiqim_turi = str(chiqim_turi) + " + " + user.username
        chiqim = Chiqim.objects.create(qayerga_id=chiqim_turi, izox=izox, user_profile=user)
        if qancha_som and kassa_var.som >= int(qancha_som):
            chiqim.kassa_som_eski = kassa_var.som
            chiqim.qancha_som = qancha_som
            kassa_var.som -= int(qancha_som)
            chiqim.kassa_som_yangi = kassa_var.som
        
        if plastik:
            chiqim.kassa_plastik_eski = kassa_var.plastik
            chiqim.plastik = plastik
            kassa_var.plastik -= int(plastik)
            chiqim.kassa_plastik_yangi = kassa_var.plastik

        if qancha_dol and kassa_var.dollar >= int(qancha_dol):
            chiqim.kassa_dol_eski = kassa_var.dollar
            chiqim.qancha_dol = qancha_dol
            kassa_var.dollar -= int(qancha_dol)
            chiqim.kassa_dol_yangi = kassa_var.dollar
            
        if qancha_hisob_raqamdan and kassa_var.hisob_raqam >= int(qancha_hisob_raqamdan):
            chiqim.kassa_hisob_raqam_eski = kassa_var.hisob_raqam
            chiqim.qancha_hisob_raqamdan = qancha_hisob_raqamdan
            kassa_var.hisob_raqam -= int(qancha_hisob_raqamdan)
            chiqim.kassa_hisob_raqam_yangi = kassa_var.hisob_raqam
            
        chiqim.save()
        kassa_var.save()

        return redirect(request.META['HTTP_REFERER'])

# for i in UserProfile.objects.filter(staff=3):
#     i.refresh_total(datetime.now().date())
# print(Cart.objects.filter(shop__date__date=datetime.now().date()))
# for i in Cart.objects.filter(shop__date__date=datetime.now().date()):
#     print(i)
#     i.save()
def one_day_price(request): 
    employe = request.GET.get('employe')
    month = request.GET.get('month')
    employes = UserProfile.objects.filter(staff=3,  daily_wage=True)
    today = datetime.today()
    
    if employe:
        employes = employes.filter(id=employe)
    if month:
        year, month = month.split('-')
        today = date(int(year), int(month), 1)
    
    
    days_of_month = int(calendar.monthrange(int(today.year), int(today.month))[1])
    dates = [x for x in range(1, days_of_month+1)]
    query = OneDayPice.objects.all()
    data = []
    for i in employes:
        dt = {
            "employee": i,
            "days": [],
            "all": OneDayPice.objects.filter(user_profile=i, is_status=True, sana__year=today.year, sana__month=today.month).aggregate(all=Coalesce(Sum('one_day_price'), 0, output_field=FloatField()))['all'],
        }
        for day in dates:
            obj, created = query.get_or_create(sana=today.replace(day=day), user_profile=i, one_day_price=i.one_day_price)
            dt['days'].append(obj)
        data.append(dt)
    
    context = {
        'chiqim_turlari': ChiqimTuri.objects.all(),
        'date': dates,
        'employee_price': query,
        'data':data
    }
    return render(request, 'day_price.html', context)





# def call_center_payment(request): 
#     employe = request.GET.get('employe')
#     month = request.GET.get('month')
#     employes = UserProfile.objects.filter(staff=6,  daily_wage=True)
#     today = datetime.today()
    
#     if employe:
#         employes = employes.filter(id=employe)
#     if month:
#         year, month = month.split('-')
#         today = date(int(year), int(month), 1)
    
    
#     days_of_month = int(calendar.monthrange(int(today.year), int(today.month))[1])
#     dates = [x for x in range(1, days_of_month+1)]
#     query = OneDayPice.objects.all()
#     data = []
#     for i in employes:
#         dt = {
#             "employee": i,
#             "days": [],
#             "all": OneDayPice.objects.filter(user_profile=i, is_status=True, sana__year=today.year, sana__month=today.month).aggregate(all=Coalesce(Sum('one_day_price'), 0))['all'],
#         }
#         for day in dates:
#             obj, created = query.get_or_create(sana=today.replace(day=day), user_profile=i, one_day_price=i.one_day_price)
#             dt['days'].append(obj)
#         data.append(dt)
    
#     context = {
#         'chiqim_turlari': ChiqimTuri.objects.all(),
#         'date': dates,
#         'employee_price': query,
#         'data':data
#     }
#     return render(request, 'day_price.html', context)




from decimal import Decimal

def one_day_price_add(request, id):
    if request.method == 'POST':
        user = UserProfile.objects.get(id=id)
        bet = request.POST.get('bet')
        sana = request.POST.get('sana')
        obj = OneDayPice.objects.filter(sana=sana, user_profile=user).last()
        obj.user_profile=user
        obj.is_status = True
        obj.sana=sana
        obj.bet=float(bet)
        obj.one_day_price=Decimal(user.one_day_price) * Decimal(bet)
        obj.save()
        return redirect("one_day_price")
    else:
        return False

def one_day_status_change(request, id):
    sana = request.POST.get('sana')
    one = OneDayPice.objects.filter(user_profile__id=id, sana=sana).last()
    one.sana=sana
    one.is_status = False
    one.save()
    return redirect("one_day_price")


def payment_user(request, id):
    if request.method == 'POST':
        
        chiqim_turi = request.POST.get('chiqim_turi')
        qancha_som = request.POST.get('qancha_som')
        qancha_dol = request.POST.get('qancha_dol')
        plastik = request.POST.get('qancha_plastik')
        
        qancha_hisob_raqamdan = request.POST.get('qancha_hisob_raqamdan')
        izox = request.POST['izox']

        kassa_var = Kassa.objects.first()

        user = UserProfile.objects.get(id=id)
        chiqim = Chiqim.objects.create(qayerga_id=chiqim_turi, izox=izox, user_profile=user)
        if qancha_som and kassa_var.som >= int(qancha_som):
            chiqim.kassa_som_eski = kassa_var.som
            chiqim.qancha_som = qancha_som
            kassa_var.som -= int(qancha_som)
            chiqim.kassa_som_yangi = kassa_var.som
        
        if plastik:
            chiqim.kassa_plastik_eski = kassa_var.plastik
            chiqim.plastik = plastik
            kassa_var.plastik -= int(plastik)
            chiqim.kassa_plastik_yangi = kassa_var.plastik

        if qancha_dol and kassa_var.dollar >= int(qancha_dol):
            chiqim.kassa_dol_eski = kassa_var.dollar
            chiqim.qancha_dol = qancha_dol
            kassa_var.dollar -= int(qancha_dol)
            chiqim.kassa_dol_yangi = kassa_var.dollar
            
        if qancha_hisob_raqamdan and kassa_var.hisob_raqam >= int(qancha_hisob_raqamdan):
            chiqim.kassa_hisob_raqam_eski = kassa_var.hisob_raqam
            chiqim.qancha_hisob_raqamdan = qancha_hisob_raqamdan
            kassa_var.hisob_raqam -= int(qancha_hisob_raqamdan)
            chiqim.kassa_hisob_raqam_yangi = kassa_var.hisob_raqam
            
        chiqim.save()
        kassa_var.save()

        return redirect('one_day_price')
    
def mobile_order(request):
    employe = request.GET.get('employe')
    month = request.GET.get('month')
    employes = MobilUser.objects.filter()
    today = datetime.today()
    
    if employe:
        employes = employes.filter(id=employe)
    if month:
        year, month = month.split('-')
        today = date(int(year), int(month), 1)
    
    
    days_of_month = int(calendar.monthrange(int(today.year), int(today.month))[1])
    dates = [x for x in range(1, days_of_month+1)]
    query = MobilPayment.objects.all()
    data = []
    for i in employes:
        total =  query.filter(sana__year=today.year, is_status=False, sana__month=today.month, m_user=i).count() * i.price_and          
        summa =  query.filter(sana__year=today.year, is_status=False, sana__month=today.month, m_user=i).count() 
        if i.after < summa:
            dt = {
                "employee": i,
                "days":[] ,
                "monthly": query.filter(sana__year=today.year, is_status=True, sana__month=today.month, m_user=i).aggregate(all=Coalesce(Sum('total_price'), 0))['all'] * i.flex_price - i.after +  i.fix_price - total,
            }
        else:
             dt = {
                "employee": i,
                "days":[] ,
                "monthly":  i.fix_price - total,
            }
        for day in dates:
            obj, created = MobilPayment.objects.get_or_create(sana=today.replace(day=day), m_user=i)
            dt['days'].append(obj)
        data.append(dt)
        
    
    context = {
        'date': dates,
        'data':data,
        'chiqim_turlari': ChiqimTuri.objects.all(),
    }
    return render(request, 'mobile_order.html', context)

def mobile_status_change(request, id):
    sana = request.POST.get('sana')
    one = MobilPayment.objects.get(m_user_id=id, sana=sana)
    one.sana=sana
    one.is_status = False
    one.save()
    return redirect("mobile_order")

def payment_user_mobil(request, id):
       if request.method == 'POST':
        
        chiqim_turi = request.POST.get('chiqim_turi')
        qancha_som = request.POST.get('qancha_som')
        qancha_dol = request.POST.get('qancha_dol')
        plastik = request.POST.get('qancha_plastik')
        
        qancha_hisob_raqamdan = request.POST.get('qancha_hisob_raqamdan')
        izox = request.POST['izox']

        kassa_var = Kassa.objects.first()

        user = MobilUser.objects.get(id=id)
        chiqim = Chiqim.objects.create(qayerga_id=chiqim_turi, izox=izox, mobil_user=user)
        if qancha_som and kassa_var.som >= int(qancha_som):
            chiqim.kassa_som_eski = kassa_var.som
            chiqim.qancha_som = qancha_som
            kassa_var.som -= int(qancha_som)
            chiqim.kassa_som_yangi = kassa_var.som
        
        if plastik:
            chiqim.kassa_plastik_eski = kassa_var.plastik
            chiqim.plastik = plastik
            kassa_var.plastik -= int(plastik)
            chiqim.kassa_plastik_yangi = kassa_var.plastik

        if qancha_dol and kassa_var.dollar >= int(qancha_dol):
            chiqim.kassa_dol_eski = kassa_var.dollar
            chiqim.qancha_dol = qancha_dol
            kassa_var.dollar -= int(qancha_dol)
            chiqim.kassa_dol_yangi = kassa_var.dollar
            
        if qancha_hisob_raqamdan and kassa_var.hisob_raqam >= int(qancha_hisob_raqamdan):
            chiqim.kassa_hisob_raqam_eski = kassa_var.hisob_raqam
            chiqim.qancha_hisob_raqamdan = qancha_hisob_raqamdan
            kassa_var.hisob_raqam -= int(qancha_hisob_raqamdan)
            chiqim.kassa_hisob_raqam_yangi = kassa_var.hisob_raqam
            
        chiqim.save()
        kassa_var.save()

        return redirect('mobile_order')

def detail_user(request, id):
    today = datetime.today()
    month = request.GET.get('month')
    user = UserProfile.objects.get(id=id)
    chiqim = Chiqim.objects.filter(user_profile=user)
    days_of_month = calendar.monthrange(int(month[:4]) if month else today.year, int(month[-2:] if month else today.month))[1]
    dates = [x for x in range(1, days_of_month+1)]
    query = AllDaySumEmployee.objects.filter(user=user,date__year=month[:4] if month else today.year, date__month=month[-2:] if month else today.month,)
    data = []
    for x in query.filter(date__day__in=dates):
        dt = {
            'date':x.date,
            'fix':query.filter(date__day__lte=x.date.day).aggregate(all=Coalesce(Sum('fix'), 0))['all'],
            'pay':x.pay,
            'summa': query.filter(date__day__lte=x.date.day).aggregate(all=Coalesce(Sum('rest'), 0))['all'],
        }
        data.append(dt)
    context = {
        'chiqim':data,
    }
    return render(request, 'user_detail_chiqim.html', context)


def detail_employee(request, id):
    
    today = datetime.today()
    user = UserProfile.objects.get(id=id)
    chiqim = AllDaySumEmployee.objects.filter(user=user)
    count_work = FlexPrice.objects.filter(is_status=True, sana__year=today.year, user_profile=user)
    count_not_work = FlexPrice.objects.filter(is_status=False, sana__year=today.year, user_profile=user)
    bonus_summa = FlexPrice.objects.filter(is_status=True, sana__year=today.year, total__gt=user.after)
    month = request.GET.get('month')

    if month:
        days_of_month = calendar.monthrange(int(month[:4]), int(month[-2:]))[1]
    else:
        days_of_month = calendar.monthrange(today.year, today.month)[1]
    dates = [x for x in range(1, days_of_month+1)]
    
    if month:
        chiqim = chiqim.filter(date__month=month[-2:])
        count_work = count_work.filter(sana__month=month[-2:])
        count_not_work=count_not_work.filter(sana__month=month[-2:])
        bonus_summa=bonus_summa.filter(sana__month=month[-2:])
    else:
        chiqim=chiqim.filter(date__year=today.year, date__month=today.month)
        count_work=count_work.filter(sana__month=today.month)
        count_not_work=count_not_work.filter(sana__month=today.month)
        bonus_summa=bonus_summa.filter(sana__month=today.month)
    
    data = []
    for x in chiqim.filter(date__day__in=dates):
        dt = {
            'date':x.date,
            'quantity':x.quantity,
            'flex_price':x.flex_price,
            'ishladi':x.ishladi,
            'fix':x.fix,
            'flex':x.flex,
            'pay':x.pay,
            'rest':chiqim.filter(date__day__lte=x.date.day).aggregate(all=Coalesce(Sum('rest'), 0))['all'],
            'summa': 0,
        }
        if x.is_status:
            dt['summa'] = chiqim.filter(date__day__lte=x.date.day).aggregate(all=Coalesce(Sum(F('summa')-F('pay')), 0 ,output_field=FloatField()))['all']
        else:
            dt['summa'] = x.summa
        data.append(dt)

    total =  FlexPrice.objects.filter(sana__year=today.year, is_status=False, sana__month=today.month, user_profile=user).count() * user.price_and                             
    all_summa = FlexPrice.objects.filter(is_status=True, sana__year=today.year, sana__month=today.month, total__gt=user.after)
    total_sum = []        
    for suma in all_summa:
            if suma.user_profile == user:
                narx = int(suma.total)-int(user.after)
                total_sum.append(narx)
    
    context = {
        'chiqim':data,
        "monthly": sum(total_sum) * user.flex_price + user.fix_price -total ,
        "fix_price":chiqim.aggregate(all=Coalesce(Sum('fix'), 0, output_field=FloatField()))['all'],
        "flex_price":chiqim.aggregate(all=Coalesce(Sum('flex'), 0, output_field=FloatField()))['all'],
        "pay":chiqim.aggregate(all=Coalesce(Sum('pay'), 0, output_field=FloatField()))['all'],
        "rest":chiqim.aggregate(all=Coalesce(Sum('rest'), 0, output_field=FloatField()))['all'],
        "summa":chiqim.aggregate(all=Coalesce(Sum('summa'), 0, output_field=FloatField()))['all'],
        "quantity":chiqim.aggregate(all=Coalesce(Sum('quantity'), 0, output_field=FloatField()))['all'],
        "ishladi":sum([i.ishladi for i in chiqim]),

        'count_work':count_work.count(),
        'count_not_work':count_not_work.count(),
        'bonus_summa':bonus_summa.aggregate(all=Coalesce(Sum('total'), 0, output_field=FloatField()))['all'],
        'fix':user.fix_price,
        'fix_summa': round(bonus_summa.aggregate(all=Coalesce(Sum('total'), Decimal('0.00')))['all'] + user.fix_price, 2)
    }
    if user.staff == 3:
        return render(request, 'detail_employee.html', context)
    else:
        return render(request, 'detail_employee2.html', context)



def detail_mobil(request, id):
    today = datetime.today()
    month = request.GET.get('month')
    if month:
        year, month = month.split('-')
        today = date(int(year), int(month), 1)
    user = MobilUser.objects.get(id=id)
    chiqim = Chiqim.objects.filter(mobil_user=user)
    context = {
        'chiqim':chiqim,
        "monthly": MobilPayment.objects.filter(m_user=user, sana__year=today.year, sana__month=today.month).aggregate(all=Coalesce(Sum('total_price'), Decimal('0.00')))['all'] * user.flex_price + user.fix_price, 
        "summa":chiqim.aggregate(all=Coalesce(Sum('qancha_som'), 0))['all'],
        "qancha_dol":chiqim.aggregate(all=Coalesce(Sum('qancha_dol'), 0))['all'],
        "plastik":chiqim.aggregate(all=Coalesce(Sum('plastik'), 0))['all'],
        "qancha_hisob_raqamdan":chiqim.aggregate(all=Coalesce(Sum('qancha_hisob_raqamdan'), 0))['all'],
    }
    return render(request, 'mobil_detail.html', context)



def desktop_kassa_view(request):
    query = DesktopKassa.objects.all()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    kassa_name = request.GET.get('kassa_name')
    desktop = DesktopKassa.objects.values('kassa_name').distinct()
    today = datetime.today().date()
    datas = []
    for i in desktop:
        today_kassa = DesktopKassa.objects.filter(kassa_name=i['kassa_name']).last()
        datas.append(today_kassa)

    if start_date and end_date:
       query = query.filter(date_time__date__gte=start_date, date_time__date__lte=end_date)
    else:
        query = query.filter(date_time__date=today)
    
    if kassa_name:
        query = query.filter(kassa_name__icontains=kassa_name)
            

    context = { 
        'kassa':query,
        'desktop':desktop,
        'today_kassa':datas,
    }
    return render(request, 'destop_kassa.html',context)





# def recieves(request):
#     recieves = Recieve.objects.all()[:10]

#     context = {
#         "recieves": recieves
#     }
#     return render(request, 'create_recieve.html', context)

from urllib.parse import urlencode, urlparse, urlunparse, parse_qs, parse_qsl
# def add_recieve(request):
#     name = request.POST.get('name' , '')
#     deliver = request.POST.get('deliver')

#     obj = Recieve.objects.create(name=name, deliver_id=deliver)
#     page = request.META['HTTP_REFERER']
#     url_parts = urlparse(page)
#     query = dict(parse_qsl(url_parts.query))
#     query['active'] = obj.id
#     redirect_url = urlunparse(url_parts._replace(query=urlencode(query)))
#     return redirect(redirect_url)

def add_recieve(request):
    name = request.POST.get('name', '')
    deliver = request.POST.get('deliver')
    filial = request.POST.get('filial')
    date = request.POST.get('date')
    valyuta = request.POST.get('valyuta')
    kurs = request.POST.get('kurs')

    obj = Recieve.objects.create(name=name, deliver_id=deliver, filial_id=filial, date=date, valyuta_id=valyuta, kurs=kurs)

    page = request.META['HTTP_REFERER']
    url_parts = urlparse(page)
    query = dict(parse_qsl(url_parts.query))
    query['active'] = obj.id 

    redirect_url = urlunparse(url_parts._replace(query=urlencode(query)))
    return redirect(redirect_url)

from django.views.decorators.http import require_POST

# @require_POST
# def add_recieve_item_view(request):
#     r = request.POST
#     recieve = int(request.POST.get('recieve'))
#     product = int(request.POST.get('product'))

#     som = int(request.POST.get('som'))
#     sotish_som = int(request.POST.get('sotish_som'))
#     # kurs = int(request.POST.get('kurs'))
#     quantity = int(request.POST.get('quantity'))
#     product = ProductFilial.objects.get(id=product)

#     price_types = product.price_types.all()

#     for i in price_types:
#         dt = request.POST.get(f'{i.id}')
#         if dt:
#             i.price = dt
#             i.save()
    
#     rec = Recieve.objects.get(id=recieve)
#     r = RecieveItem.objects.create(
#         recieve=rec,
#         product=product,
#         som=som,
#         sotish_som=sotish_som,
#         quantity=quantity
#     )
#     if rec.status == 0:
#         rec.status=1
#         rec.save()
   
#     rec.som += som * quantity
#     rec.sum_sotish_som += sotish_som * quantity
#     rec.save()

#     # s = self.get_serializer_class()(r)
#     return redirect(request.META['HTTP_REFERER'])


@require_POST
def add_recieve_item_view(request):
    recieve = int(request.POST.get('recieve'))
    product = int(request.POST.get('product'))
    quantity = float(request.POST.get('quantity'))
    rec = Recieve.objects.get(id=recieve)
    # item_id = request.POST.get("item")
    # item = RecieveItem.objects.get(id=item_id)
    product = ProductFilial.objects.get(id=product)
    item = RecieveItem.objects.create(
        recieve=rec,
        product=product,
        quantity=quantity
    )
    quantity = request.POST.get("quantity").replace(',','.')
    if quantity:
        item.quantity = float(quantity)
   
    for key, value in request.POST.items():
        if key.startswith("br_"):
            _, valuta_id, id = key.split("_")
            valyuta = Valyuta.objects.get(id=valuta_id)

           

            bring_price_obj, _ = ProductBringPrice.objects.get_or_create(
            valyuta=valyuta,
            product=item.product,
            recieveitem=item
            )
            bring_price_obj.price = float(value)
            bring_price_obj.save()


    for key, value in request.POST.items():
        if key.startswith("price_"):
            _, type_id, valuta_id = key.split("_")
            # price_type = PriceType.objects.get(id=type_id)
            valyuta = Valyuta.objects.get(id=valuta_id)
            ppt = ProductPriceType.objects.get(id=type_id)
            ppt.price = float(value)
            ppt.save()

    
    item.save()

    if rec.status == 0:
        rec.status=1
        rec.save()
   
    rec.save()

    return redirect(request.META.get('HTTP_REFERER'))




# @require_POST
# def edit_recieve_item_view(request):
#     r = request.POST
#     item = int(request.POST.get('item'))

#     som = int(request.POST.get('som'))
#     sotish_som = int(request.POST.get('sotish_som'))
#     # kurs = int(request.POST.get('kurs'))
#     quantity = int(request.POST.get('quantity'))
#     item = RecieveItem.objects.get(id=item)

#     price_types = item.product.price_types.all()

#     for i in price_types:
#         dt = request.POST.get(f'{i.id}')
#         if dt:
#             i.price = dt
#             i.save()
    
#     rec = item.recieve
#     item.som = som
#     item.sotish_som = sotish_som
#     item.quantity = quantity
#     item.save()

#     if rec.status == 0:
#         rec.status=1
#         rec.save()
   
#     rec.som += som * quantity
#     rec.sum_sotish_som += sotish_som * quantity
#     rec.save()

#     # s = self.get_serializer_class()(r)
#     return redirect(request.META['HTTP_REFERER'])


@require_POST
def edit_recieve_item_view(request):
    item_id = request.POST.get("item")
    item = RecieveItem.objects.get(id=item_id)
    
    quantity = request.POST.get("quantity")
    if quantity:
        item.quantity = float(quantity)
   
    for key, value in request.POST.items():
        if key.startswith("br_"):
            _, valuta_id, id = key.split("_")
            valyuta = Valyuta.objects.get(id=valuta_id)
            if id:
                bring_price_obj = ProductBringPrice.objects.get(id=id)
            else:
                bring_price_obj, _ = ProductBringPrice.objects.get_or_create(
                valyuta=valyuta,
                product=item.product,
                recieveitem=item
            )
            bring_price_obj.price = float(value)
            bring_price_obj.save()

    item.save()

    for key, value in request.POST.items():
        if key.startswith("price_"):
            _, type_id, valuta_id = key.split("_")
            # price_type = PriceType.objects.get(id=type_id)
            valyuta = Valyuta.objects.get(id=valuta_id)
            ppt = ProductPriceType.objects.get(id=type_id)
            ppt.price = float(value)
            ppt.save()

    return redirect(request.META.get('HTTP_REFERER'))


def get_product_prices(request):
    product_id = request.GET.get('product')
    try:
        product = ProductFilial.objects.get(id=product_id)
    except ProductFilial.DoesNotExist:
        return JsonResponse([], safe=False)


    data = {
        'bring_prices': product.bring_prices,
        'sell_prices': product.pricetypevaluta_prices,
        'price_types': [i.name for i in PriceType.objects.all()],
    }

    return JsonResponse(data, safe=False)




def delete_recieve(request, id):
    Recieve.objects.get(id=id).delete()
    return redirect(request.META['HTTP_REFERER'])


def delete_recieve_item(request, id):
    item = RecieveItem.objects.get(id=id)
    recieve = item.recieve
    item.delete()
    # recieve.som -= item.som * item.quantity
    # recieve.sum_sotish_som -= item.sotish_som * item.quantity
    recieve.save()
    return redirect(request.META['HTTP_REFERER'])



@require_POST
def add_recieve_expanse(request):
    recieve_id = request.POST.get("recieve_id")
    recieve = get_object_or_404(Recieve, id=recieve_id)
    RecieveExpanses.objects.create(
        recieve=recieve,
        type_id=request.POST.get("type"),
        summa=request.POST.get("summa"),
        valyuta_id=request.POST.get("valyuta"),
        externaluser_id=request.POST.get("externaluser") or None,
        comment=request.POST.get("comment")
    )
    return redirect(request.META.get('HTTP_REFERER'))

@require_POST
def edit_recieve_expanse(request, pk):
    expanse = get_object_or_404(RecieveExpanses, id=pk)
    # expanse.type_id = request.POST.get("type")
    expanse.summa = request.POST.get("summa")
    # expanse.valyuta_id = request.POST.get("valyuta")
    # expanse.externaluser_id = request.POST.get("externaluser") or None
    # expanse.comment = request.POST.get("comment")
    expanse.save()
    return redirect(request.META.get('HTTP_REFERER'))

@require_POST
def delete_recieve_expanse(request, pk):
    expanse = get_object_or_404(RecieveExpanses, id=pk)
    expanse.delete()
    return redirect(request.META.get('HTTP_REFERER'))


def add_expanse_type(request):
    name = request.POST.get('name')
    RecieveExpanseTypes.objects.create(name=name)
    return redirect(request.META.get('HTTP_REFERER'))



def new_product_add(request):
    name = request.POST.get('name')
    deliver = request.POST.get('deliver')
    # som = request.POST.get('som')
    # sotish_som = request.POST.get('sotish_som')
    barcode = request.POST.get('barcode')
    group = request.POST.get('group')
    measurement = request.POST.get('measurement')
    min_count = request.POST.get('min_count')
    # quantity = request.POST.get('quantity')
    filial_id = request.POST.get('filial_id')
    pr = ProductFilial.objects.create(
        name=name,
        # preparer=preparer,
        # som=som,
        # sotish_som=sotish_som,
        barcode=barcode,
        group_id=group,
        measurement=measurement,
        min_count=min_count,
        # quantity=quantity,
        filial_id=filial_id if filial_id else 4
    )
    if deliver:
        pr.deliver.add(Deliver.objects.get(id=deliver))
    pr.save()
    return redirect(request.META['HTTP_REFERER'])


# for i in UserProfile.objects.filter(id=11):
#     i.refresh_total('2024-06-26')


def kassa_detail_som(request):
    bugun = datetime.now()
    kassa_var = Kassa.objects.first()
    expenses = FilialExpense.objects.all()
    branches = Filial.objects.all()
    
    shu_oylik_chiqimlar = Chiqim.objects.filter(Q(qancha_som__gt=0)).order_by('-id')
    shu_oylik_kirimlar = Kirim.objects.filter(Q(qancha_som__gt=0)).order_by('-id')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    deliver = request.GET.get('deliver')
    chiqim_turi = request.GET.get('chiqim_turi')

    expanse_category = request.GET.get('expanse_category')
    if start_date and end_date:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qachon__gte=start_date, qachon__lte=end_date).order_by('-qachon')
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qachon__gte=start_date, qachon__lte=end_date).order_by('-qachon')
        expenses = expenses.filter(created_at__range=(start_date, end_date)).order_by('-created_at')
    else:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qachon__year=bugun.year, qachon__month=bugun.month).order_by('-qachon')
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qachon__year=bugun.year, qachon__month=bugun.month).order_by('-qachon')
        expenses = expenses.filter(created_at__year=bugun.year, created_at__month=bugun.month).order_by('-created_at')
    if deliver:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(deliver_id=deliver)
    if chiqim_turi:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qayerga_id=chiqim_turi)
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qayerga_id=chiqim_turi)
    if expanse_category:
        expenses = expenses.filter(category_id=expanse_category)
    chiqim_turlari = ChiqimTuri.objects.all()
    chiqim_total_som = shu_oylik_chiqimlar.aggregate(Sum('qancha_som'))['qancha_som__sum']
    kirim_total_som = shu_oylik_kirimlar.aggregate(Sum('qancha_som'))['qancha_som__sum']
    chiqim_total_som_yangi = shu_oylik_chiqimlar.aggregate(Sum('kassa_som_yangi'))['kassa_som_yangi__sum']
    kirim_total_som_yangi = shu_oylik_kirimlar.aggregate(Sum('kassa_som_yangi'))['kassa_som_yangi__sum']


    
    birlashtirilgan_malumotlar = sorted(chain(shu_oylik_chiqimlar, shu_oylik_kirimlar),key=lambda obj: obj.qachon,reverse=True)
    
    content = {
        'birlashtirilgan_malumotlar':birlashtirilgan_malumotlar,
        'kassa_active':'active',
        'kassa_true':'true',
        "chiqim_turlari":chiqim_turlari,
        'kassa':kassa_var,
        'kirim_total_som': kirim_total_som,
        'chiqim_total_som': chiqim_total_som,
        'chiqim_total_som_yangi': chiqim_total_som_yangi,
        'kirim_total_som_yangi': kirim_total_som_yangi,
        'filial': "active",
        'filial_t': "true",
        'filials': branches,
        'total_expenses': expenses.aggregate(foo=Coalesce(Sum('total_sum'),0))['foo'],
        'expenses': expenses,
        'chiqim_turi': ChiqimTuri.objects.all(),
        'expanse_category': FilialExpenseCategory.objects.all(),
        'delivers': Deliver.objects.all(),
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'deliver': int(deliver) if deliver else 0,
            'chiqim_turi': int(chiqim_turi) if chiqim_turi else 0,
            'expanse_category': int(expanse_category) if expanse_category else 0
        }
    }
    content['dollar_kurs'] = Course.objects.last().som
    return render(request, 'kassa_detail.html', content)


def kassa_detail_dollar(request):
    bugun = datetime.now()
    hodimlar = HodimModel.objects.all()
    kassa_var = Kassa.objects.first()
    expenses = FilialExpense.objects.all()
    branches = Filial.objects.all()

    hodimlar_qarz = []
    shu_oylik_chiqimlar = Chiqim.objects.filter(Q(qancha_dol__gt=0)).order_by('-id')
    shu_oylik_kirimlar = Kirim.objects.filter(Q(qancha_dol__gt=0)).order_by('-id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    deliver = request.GET.get('deliver')
    chiqim_turi = request.GET.get('chiqim_turi')
    expanse_category = request.GET.get('expanse_category')
    if start_date and end_date:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qachon__gte=start_date, qachon__lte=end_date).order_by('-qachon')
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qachon__gte=start_date, qachon__lte=end_date).order_by('-qachon')
        expenses = expenses.filter(created_at__range=(start_date, end_date)).order_by('-created_at')
    else:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qachon__year=bugun.year, qachon__month=bugun.month).order_by('-qachon')
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qachon__year=bugun.year, qachon__month=bugun.month).order_by('-qachon')
        expenses = expenses.filter(created_at__year=bugun.year, created_at__month=bugun.month).order_by('-created_at')

    if deliver:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(deliver_id=deliver)
    if chiqim_turi:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qayerga_id=chiqim_turi)
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qayerga_id=chiqim_turi)
    
    if expanse_category:
        expenses = expenses.filter(category_id=expanse_category)

    chiqim_turlari = ChiqimTuri.objects.all()
    
    chiqim_total_dollar = shu_oylik_chiqimlar.aggregate(Sum('qancha_dol'))['qancha_dol__sum']
    kirim_total_dollar = shu_oylik_kirimlar.aggregate(Sum('qancha_dol'))['qancha_dol__sum']
    chiqim_total_dol_yangi = shu_oylik_chiqimlar.aggregate(Sum('kassa_dol_yangi'))['kassa_dol_yangi__sum']
    kirim_total_dol_yangi = shu_oylik_kirimlar.aggregate(Sum('kassa_dol_yangi'))['kassa_dol_yangi__sum']

    birlashtirilgan_malumotlar = sorted(chain(shu_oylik_chiqimlar, shu_oylik_kirimlar),key=lambda obj: obj.qachon,reverse=True)

    content = {
        'kassa_active':'active',
        'kassa_true':'true',
        'barcha_hodimlar':hodimlar,
        'birlashtirilgan_malumotlar':birlashtirilgan_malumotlar,
        "chiqim_turlari":chiqim_turlari,
        'hodimlar_qarz':hodimlar_qarz,
        'kassa':kassa_var,
        'chiqim_total_dollar': chiqim_total_dollar,
        'kirim_total_dollar': kirim_total_dollar,
        'kirim_total_dol_yangi': kirim_total_dol_yangi,
        'chiqim_total_dol_yangi': chiqim_total_dol_yangi,
        'filial': "active",
        'filial_t': "true",
        'filials': branches,
        'expenses': expenses,
        'chiqim_turi': ChiqimTuri.objects.all(),
        'expanse_category': FilialExpenseCategory.objects.all(),
        'delivers': Deliver.objects.all(),
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'deliver': int(deliver) if deliver else 0,
            'chiqim_turi': int(chiqim_turi) if chiqim_turi else 0,
            'expanse_category': int(expanse_category) if expanse_category else 0
        }
    }
    content['dollar_kurs'] = Course.objects.last().som
    return render(request, 'kassa_detail_dollar.html', content)

def kassa_detail_plastik(request):
    bugun = datetime.now()
    hodimlar = HodimModel.objects.all()
    kassa_var = Kassa.objects.first()
    expenses = FilialExpense.objects.all()
    branches = Filial.objects.all()

    hodimlar_qarz = []
    shu_oylik_chiqimlar = Chiqim.objects.filter(Q(plastik__gt=0 )).order_by('-id')
    shu_oylik_kirimlar = Kirim.objects.filter(Q(plastik__gt=0 )).order_by('-id')
    # if request.method == 'POST':
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    deliver = request.GET.get('deliver')
    chiqim_turi = request.GET.get('chiqim_turi')
    expanse_category = request.GET.get('expanse_category')
    if start_date and end_date:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qachon__gte=start_date, qachon__lte=end_date).order_by('-qachon')
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qachon__gte=start_date, qachon__lte=end_date).order_by('-qachon')
        expenses = expenses.filter(created_at__range=(start_date, end_date)).order_by('-created_at')
    else:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qachon__year=bugun.year, qachon__month=bugun.month).order_by('-qachon')
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qachon__year=bugun.year, qachon__month=bugun.month).order_by('-qachon')
        expenses = expenses.filter(created_at__year=bugun.year, created_at__month=bugun.month).order_by('-created_at')

    if deliver:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(deliver_id=deliver)
    if chiqim_turi:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qayerga_id=chiqim_turi)
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qayerga_id=chiqim_turi)
    
    if expanse_category:
        expenses = expenses.filter(category_id=expanse_category)

    chiqim_turlari = ChiqimTuri.objects.all()
    
    chiqim_plastik = shu_oylik_chiqimlar.aggregate(Sum('plastik'))['plastik__sum']
    kirim_plastik = shu_oylik_kirimlar.aggregate(Sum('plastik'))['plastik__sum']
    chiqim_total_kassa_plastik_yangi = shu_oylik_chiqimlar.aggregate(Sum('kassa_plastik_yangi'))['kassa_plastik_yangi__sum']
    kirim_total_kassa_plastik_yangi = shu_oylik_kirimlar.aggregate(Sum('kassa_plastik_yangi'))['kassa_plastik_yangi__sum']

    birlashtirilgan_malumotlar = sorted(chain(shu_oylik_chiqimlar, shu_oylik_kirimlar),key=lambda obj: obj.qachon,reverse=True)

    content = {
        'kassa_active':'active',
        'kassa_true':'true',
        'birlashtirilgan_malumotlar':birlashtirilgan_malumotlar,
        'barcha_hodimlar':hodimlar,
        'shu_oylik_chiqimlar':shu_oylik_chiqimlar,
        'shu_oylik_kirimlar':shu_oylik_kirimlar,
        "chiqim_turlari":chiqim_turlari,
        'hodimlar_qarz':hodimlar_qarz,
        'kassa':kassa_var,
        'chiqim_plastik': chiqim_plastik,
        'kirim_plastik': kirim_plastik,
        'chiqim_total_kassa_plastik_yangi': chiqim_total_kassa_plastik_yangi,
        'kirim_total_kassa_plastik_yangi': kirim_total_kassa_plastik_yangi,
        'filial': "active",
        'filial_t': "true",
        'filials': branches,
        # 'current_filial': current_filial,
        'expenses': expenses,
        'chiqim_turi': ChiqimTuri.objects.all(),
        'expanse_category': FilialExpenseCategory.objects.all(),
        'delivers': Deliver.objects.all(),
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'deliver': int(deliver) if deliver else 0,
            'chiqim_turi': int(chiqim_turi) if chiqim_turi else 0,
            'expanse_category': int(expanse_category) if expanse_category else 0
        }
    }
    content['dollar_kurs'] = Course.objects.last().som
    return render(request, 'kassa_detail_plastik.html', content)

def kassa_detail_hisob_raqam(request):
    bugun = datetime.now()
    hodimlar = HodimModel.objects.all()
    kassa_var = Kassa.objects.first()
    expenses = FilialExpense.objects.all()
    branches = Filial.objects.all()

    hodimlar_qarz = []
    shu_oylik_chiqimlar = Chiqim.objects.filter(Q(qancha_hisob_raqamdan__gt=0 )).order_by('-id')
    shu_oylik_kirimlar = Kirim.objects.filter(Q(qancha_hisob_raqamdan__gt=0)).order_by('-id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    deliver = request.GET.get('deliver')
    chiqim_turi = request.GET.get('chiqim_turi')
    expanse_category = request.GET.get('expanse_category')
    if start_date and end_date:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qachon__gte=start_date, qachon__lte=end_date).order_by('-qachon')
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qachon__gte=start_date, qachon__lte=end_date).order_by('-qachon')
        expenses = expenses.filter(created_at__range=(start_date, end_date)).order_by('-created_at')
    else:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qachon__year=bugun.year, qachon__month=bugun.month).order_by('-qachon')
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qachon__year=bugun.year, qachon__month=bugun.month).order_by('-qachon')
        expenses = expenses.filter(created_at__year=bugun.year, created_at__month=bugun.month).order_by('-created_at')

    if deliver:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(deliver_id=deliver)
    if chiqim_turi:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qayerga_id=chiqim_turi)
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qayerga_id=chiqim_turi)
    
    if expanse_category:
        expenses = expenses.filter(category_id=expanse_category)

    chiqim_turlari = ChiqimTuri.objects.all()
    

    chiqim_hisob_raqam_total = shu_oylik_chiqimlar.aggregate(Sum('qancha_hisob_raqamdan'))['qancha_hisob_raqamdan__sum']
    kirim_hisob_raqam_total = shu_oylik_kirimlar.aggregate(Sum('qancha_hisob_raqamdan'))['qancha_hisob_raqamdan__sum']
    chiqim_total_kassa_hisob_raqam_yangi = shu_oylik_chiqimlar.aggregate(Sum('kassa_hisob_raqam_yangi'))['kassa_hisob_raqam_yangi__sum']
    kirim_total_kassa_hisob_raqam_yangi = shu_oylik_kirimlar.aggregate(Sum('kassa_hisob_raqam_yangi'))['kassa_hisob_raqam_yangi__sum']

    birlashtirilgan_malumotlar = sorted(chain(shu_oylik_chiqimlar, shu_oylik_kirimlar),key=lambda obj: obj.qachon,reverse=True)

    
    content = {
        'kassa_active':'active',
        'kassa_true':'true',
        'birlashtirilgan_malumotlar':birlashtirilgan_malumotlar,
        'barcha_hodimlar':hodimlar,
        'shu_oylik_chiqimlar':shu_oylik_chiqimlar,
        'shu_oylik_kirimlar':shu_oylik_kirimlar,
        "chiqim_turlari":chiqim_turlari,
        'hodimlar_qarz':hodimlar_qarz,
        'kassa':kassa_var,
        'chiqim_hisob_raqam_total': chiqim_hisob_raqam_total,
        'kirim_hisob_raqam_total': kirim_hisob_raqam_total,
        'chiqim_total_kassa_hisob_raqam_yangi': chiqim_total_kassa_hisob_raqam_yangi,
        'kirim_total_kassa_hisob_raqam_yangi': kirim_total_kassa_hisob_raqam_yangi,
        'filial': "active",
        'filial_t': "true",
        'filials': branches,
        'expenses': expenses,
        'chiqim_turi': ChiqimTuri.objects.all(),
        'expanse_category': FilialExpenseCategory.objects.all(),
        'delivers': Deliver.objects.all(),
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'deliver': int(deliver) if deliver else 0,
            'chiqim_turi': int(chiqim_turi) if chiqim_turi else 0,
            'expanse_category': int(expanse_category) if expanse_category else 0
        }
    }
    content['dollar_kurs'] = Course.objects.last().som
    return render(request, 'kassa_detail_hisob_raqam.html', content)





def kassa_is_approved(request):
    bugun = datetime.now()
    hodimlar = HodimModel.objects.all()
    kassa_var = Kassa.objects.first()
    expenses = FilialExpense.objects.all()
    branches = Filial.objects.all()
    hodimlar_qarz = []
    shu_oylik_chiqimlar = Chiqim.objects.filter(is_approved=False).order_by('-id')
    shu_oylik_kirimlar = Kirim.objects.filter(is_approved=False).order_by('-id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    deliver = request.GET.get('deliver')
    chiqim_turi = request.GET.get('chiqim_turi')
    expanse_category = request.GET.get('expanse_category')
    if start_date and end_date:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qachon__gte=start_date, qachon__lte=end_date).order_by('-qachon')
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qachon__gte=start_date, qachon__lte=end_date).order_by('-qachon')
        expenses = expenses.filter(created_at__range=(start_date, end_date)).order_by('-created_at')
    else:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qachon__year=bugun.year, qachon__month=bugun.month).order_by('-qachon')
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qachon__year=bugun.year, qachon__month=bugun.month).order_by('-qachon')
        expenses = expenses.filter(created_at__year=bugun.year, created_at__month=bugun.month).order_by('-created_at')

    if deliver:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(deliver_id=deliver)
    if chiqim_turi:
        shu_oylik_chiqimlar = shu_oylik_chiqimlar.filter(qayerga_id=chiqim_turi)
        shu_oylik_kirimlar = shu_oylik_kirimlar.filter(qayerga_id=chiqim_turi)
    
    if expanse_category:
        expenses = expenses.filter(category_id=expanse_category)

    chiqim_turlari = ChiqimTuri.objects.all()
    
    chiqim_total_som = shu_oylik_chiqimlar.aggregate(Sum('qancha_som'))['qancha_som__sum']
    chiqim_total_dollar = shu_oylik_chiqimlar.aggregate(Sum('qancha_dol'))['qancha_dol__sum']
    chiqim_hisob_raqam_total = shu_oylik_chiqimlar.aggregate(Sum('qancha_hisob_raqamdan'))['qancha_hisob_raqamdan__sum']
    chiqim_plastik = shu_oylik_chiqimlar.aggregate(Sum('plastik'))['plastik__sum']
    
    kirim_total_som = shu_oylik_kirimlar.aggregate(Sum('qancha_som'))['qancha_som__sum']
    kirim_total_dollar = shu_oylik_kirimlar.aggregate(Sum('qancha_dol'))['qancha_dol__sum']
    kirim_hisob_raqam_total = shu_oylik_kirimlar.aggregate(Sum('qancha_hisob_raqamdan'))['qancha_hisob_raqamdan__sum']
    kirim_plastik = shu_oylik_kirimlar.aggregate(Sum('plastik'))['plastik__sum']

    for hodim in hodimlar:
        qarz_som = 0
        qarz_dol = 0
        for q in hodim.hodimqarz_set.filter(tolandi=False):
            qarz_som += q.qancha_som
            qarz_dol += q.qancha_dol

        dt = {
            'id': hodim.id,
            'ism_familya':hodim.toliq_ism_ol(),
            'filial':hodim.filial.name,
            'qarz_som':qarz_som,
            'qarz_dol':qarz_dol,   
        }

        hodimlar_qarz.append(dt)
    
    total_expenses = expenses.aggregate(foo=Coalesce(
        Sum('total_sum'),
        0
    ))['foo']

    hodimlar_royxat = [
        hodim
        for hodim in hodimlar
        if not OylikTolov.objects.filter(
            hodim_id=hodim.id, sana__year=bugun.year, sana__month=bugun.month
        ).exists()
    ]

    content = {
        'kassa_active':'active',
        'kassa_true':'true',
        'hodimlar':hodimlar_royxat,
        'barcha_hodimlar':hodimlar,
        'shu_oylik_chiqimlar':shu_oylik_chiqimlar,
        'shu_oylik_kirimlar':shu_oylik_kirimlar,
        "chiqim_turlari":chiqim_turlari,
        'hodimlar_qarz':hodimlar_qarz,
        'kassa':kassa_var,
        'chiqim_total_som': chiqim_total_som,
        'chiqim_total_dollar': chiqim_total_dollar,
        'chiqim_hisob_raqam_total': chiqim_hisob_raqam_total,
        'kirim_total_som': kirim_total_som,
        'kirim_total_dollar': kirim_total_dollar,
        'kirim_hisob_raqam_total': kirim_hisob_raqam_total,
        'chiqim_plastik': chiqim_plastik,
        'kirim_plastik': kirim_plastik,
        'filial': "active",
        'filial_t': "true",
        'filials': branches,
        # 'current_filial': current_filial,
        'total_expenses': total_expenses,
        'expenses': expenses,
        'chiqim_turi': ChiqimTuri.objects.all(),
        'expanse_category': FilialExpenseCategory.objects.all(),
        'delivers': Deliver.objects.all(),
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'deliver': int(deliver) if deliver else 0,
            'chiqim_turi': int(chiqim_turi) if chiqim_turi else 0,
            'expanse_category': int(expanse_category) if expanse_category else 0
        }
    }
    content['dollar_kurs'] = Course.objects.last().som
    return render(request, 'kassa_is_approved.html', content)


def change_chiqim_is_approved(request,id):
    is_approved = request.POST.get('is_approved', False)
    chiqim = Chiqim.objects.get(id=id)
    chiqim.is_approved=is_approved
    chiqim.save()
    return redirect(request.META['HTTP_REFERER'])


def change_kirim_is_approved(request,id):
    is_approved = request.POST.get('is_approved')
    kirim = Kirim.objects.get(id=id)
    kirim.is_approved=True if is_approved == 'on' else False
    kirim.save()
    return redirect(request.META['HTTP_REFERER'])




def accept_expanse(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        if id:
            obj = DesktopChiqim.objects.get(id=id)
            qayerga = obj.qayerga
            qancha_som = obj.qancha_som
            qancha_dol = obj.qancha_dol
            plastik = obj.plastik
            qancha_hisob_raqamdan = obj.qancha_hisob_raqamdan
            izox = obj.izox
            qachon = obj.qachon
            user_profile = obj.user_profile
            success = True
            
            chiqim = Chiqim.objects.create(
                qayerga=qayerga,
                izox=izox,
                qachon=qachon,
                user_profile=user_profile,
            )
            kassa_var = Kassa.objects.first()
            if qancha_som and kassa_var.som >= int(qancha_som):
                chiqim.kassa_som_eski = kassa_var.som
                chiqim.qancha_som = qancha_som
                kassa_var.som -= int(qancha_som)
                chiqim.kassa_som_yangi = kassa_var.som
            
            
            if plastik and kassa_var.plastik >= int(plastik):
                chiqim.kassa_plastik_eski = kassa_var.plastik
                chiqim.plastik = plastik
                kassa_var.plastik -= int(plastik)
                chiqim.kassa_plastik_yangi = kassa_var.plastik

            if qancha_dol and kassa_var.dollar >= int(qancha_dol):
                chiqim.kassa_dol_eski = kassa_var.dollar
                chiqim.qancha_dol = qancha_dol
                kassa_var.dollar -= int(qancha_dol)
                chiqim.kassa_dol_yangi = kassa_var.dollar
                
            if qancha_hisob_raqamdan and kassa_var.hisob_raqam >= int(qancha_hisob_raqamdan):
                chiqim.kassa_hisob_raqam_eski = kassa_var.hisob_raqam
                chiqim.qancha_hisob_raqamdan = qancha_hisob_raqamdan
                kassa_var.hisob_raqam -= int(qancha_hisob_raqamdan)
                chiqim.kassa_hisob_raqam_yangi = kassa_var.hisob_raqam
            
            if kassa_var.som < 0 or kassa_var.plastik < 0 or kassa_var.dollar < 0 or kassa_var.hisob_raqam < 0:
                chiqim.delete()
                messages.error(request, "Kassada mablag' yetarli emas")
                return redirect(request.META['HTTP_REFERER'])
            obj.is_approved = True
            obj.save()
            chiqim.save()
            kassa_var.save()
            return redirect(request.META['HTTP_REFERER'])

        # Chiqim.objects.create(qayerga.obj.qayerga,)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    chiqim_turi = request.GET.get('chiqim_turi')
    bugun = datetime.now()
    expenses = DesktopChiqim.objects.filter(is_approved=False)

    if start_date and end_date:
        expenses = expenses.filter(qachon__gte=start_date, qachon__lte=end_date).order_by('-qachon')
    else:
        expenses = expenses.filter(qachon__year=bugun.year, qachon__month=bugun.month).order_by('-qachon')

    if chiqim_turi:
        expenses = expenses.filter(qayerga_id=chiqim_turi)

    totals = {
        'qancha_som': sum([i.qancha_som for i in expenses]),
        'qancha_dol': sum([i.qancha_dol for i in expenses]),
        'plastik': sum([i.plastik for i in expenses]),
        'qancha_hisob_raqamdan': sum([i.qancha_hisob_raqamdan for i in expenses]),
    }

    context = {
        'expenses': expenses,
        'totals': totals,
        'chiqim_turi': ChiqimTuri.objects.all(),
    }
    return render(request, 'accept_expanse.html', context)


def create_deliver(request):
    name = request.POST.get('name')
    phone1 = request.POST.get('phone1')
    phone2 = request.POST.get('phone2')

    Deliver.objects.create(name=name, phone1=phone1, phone2=phone2)
    messages.success(request, 'Muvaffaqiyatli yaratildi')
    return redirect(request.META['HTTP_REFERER'])
# for i in Kirim.objects.filter(qancha_hisob_raqamdan__gt=0):
#     i.save()






def top_products(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    seller_id = [int(i) for i in request.GET.getlist('seller')  if i != '']
    hudud = [int(i) for i in request.GET.getlist('hudud')  if i != '']
    # type_country = [int(i) for i in request.GET.getlist('country')  if i != '']


    orders = Shop.objects.all()
    
    if start_date and end_date:
        orders = orders.filter(date__gte=start_date, date__lte=end_date)
    else:
        orders = orders.filter(date__gte=datetime.now().date().replace(day=1))
    
    if hudud:
        orders = orders.filter(debtor__teritory__in=hudud)
    
    if seller_id:
        orders = orders.filter(saler_id__in=seller_id)
    
        
    baskets = Cart.objects.filter(shop__in=orders)

    # if type_country:
    #     baskets = baskets.filter(product__product__type_country__in=type_country)

    
    

    products = ProductFilial.objects.filter(cart__in=baskets).distinct()
    
    data = []

    for i in products:
        data.append({
            'store': i,
            'total_price': baskets.filter(product=i).aggregate(foo=Coalesce(Sum('total'), float(0), output_field=FloatField()))['foo'],
            'foyda': baskets.filter(product=i).aggregate(foo=Coalesce(Sum(F('total') - (F('quantity') * F('bring_price'))), float(0), output_field=FloatField()))['foo'],
            'total_count': baskets.filter(product=i).aggregate(foo=Coalesce(Sum('quantity'), float(0), output_field=FloatField()))['foo'],
        })
        
    
    totals = {
        'total_price': baskets.aggregate(foo=Coalesce(Sum('total'), float(0), output_field=FloatField()))['foo'],
        'foyda': baskets.aggregate(foo=Coalesce(Sum(F('total') - (F('quantity') * F('bring_price'))), float(0), output_field=FloatField()))['foo'],
        'total_count': baskets.aggregate(foo=Coalesce(Sum('quantity'), float(0), output_field=FloatField()))['foo'],
    }

    filters = {
        'start_date': start_date,
        'end_date': end_date,
        'seller': seller_id,
        'hudud': hudud,
    }

    context = {
        'totals': totals,
        'filters': filters,
        'data': data,
        'viloyatlar': Teritory.objects.all(),
        # 'countries': countries,
        # 'products': Store.objects.all(),
        'sellers': UserProfile.objects.filter(staff=3)
    }

    return render(request, 'top_products.html', context)







def top_debtors(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    seller_id = [int(i) for i in request.GET.getlist('seller')  if i != '']
    hudud = [int(i) for i in request.GET.getlist('hudud')  if i != '']

    orders = Shop.objects.all()
    
    if start_date and end_date:
        orders = orders.filter(date__gte=start_date, date__lte=end_date)
    else:
        orders = orders.filter(date__gte=datetime.now().date().replace(day=1))
    
    if hudud:
        orders = orders.filter(debtor__teritory__in=hudud)
    
    if seller_id:
        orders = orders.filter(saler_id__in=seller_id)
    
    valyuta = Valyuta.objects.all()
        
    baskets = Cart.objects.filter(shop__in=orders)

    debtors = Debtor.objects.filter(debtor_shops__in=orders).distinct()
    
    data = []

    for i in debtors:
        dt = {
            'debtor': i,
            'order_count': orders.filter(debtor=i).count(),
            'total_count': baskets.filter(shop__debtor=i).aggregate(foo=Coalesce(Sum('quantity'), float(0), output_field=FloatField()))['foo'],
            'valyuta': []

            # 'total_price': baskets.filter(shop__debtor=i).aggregate(foo=Coalesce(Sum('total'), float(0), output_field=FloatField()))['foo'],
            # 'foyda': baskets.filter(shop__debtor=i).aggregate(foo=Coalesce(Sum(F('total') - (F('quantity') * F('bring_price'))), float(0), output_field=FloatField()))['foo'],
        }
        for x in valyuta:
            summa =  baskets.filter(shop__debtor=i, shop__valyuta=x).aggregate(
                         total=Coalesce(Sum('total'), 0,output_field=IntegerField())
                )['total']
            foyda = sum([
                    cart.foyda_total for cart in baskets
                ])
            val = {
                'valyuta': x,
                'summa':summa,
                'foyda':foyda,
            }
            # if x.is_dollar:
                # val['foyda'] = RecieveItem.objects.filter(product=)
            dt['valyuta'].append(val)
        data.append(dt)
        
        
        
    totals = {
        'order_count': orders.count(),
        'total_price': baskets.aggregate(foo=Coalesce(Sum('total'), float(0), output_field=FloatField()))['foo'],
        'foyda': baskets.aggregate(foo=Coalesce(Sum(F('total') - (F('quantity') * F('bring_price'))), float(0), output_field=FloatField()))['foo'],
        'total_count': baskets.aggregate(foo=Coalesce(Sum('quantity'), float(0), output_field=FloatField()))['foo'],
    }

    filters = {
        'start_date': start_date,
        'end_date': end_date,
        'seller': seller_id,
        'hudud': hudud,
    }

    context = {
        'totals': totals,
        'filters': filters,
        'data': data,
        'valyuta':valyuta,
        'viloyatlar': Teritory.objects.all(),
        'sellers': UserProfile.objects.filter(staff=3).distinct()
    }

    return render(request, 'top_debtors.html', context)

def detail_top_debtors(request, id):
    cart = Cart.objects.filter(shop__debtor_id=id)
    valyuta = request.GET.get('valyuta')
    if valyuta:
        cart = cart.filter(shop__valyuta_id=valyuta)
    
    filters = {
        'valyuta':valyuta
    }
    totals = {
        'quantity':cart.aggregate(all=Coalesce(Sum('quantity'), 0, output_field=IntegerField()))['all'],
        'total':cart.aggregate(all=Coalesce(Sum('total'), 0, output_field=IntegerField()))['all'],
    }
    context = {
        'cart':cart,
        'totals':totals,
        'valyuta':Valyuta.objects.all(),
        'filters':filters,
    }
    return render(request, 'detail_top_debtors.html', context)



def users_restrictions(request):
    context = {
        'use':UserProfile.objects.all().order_by('-id'),
    }
    return render(request, 'users_restrictions.html', context)


def users_restrictions_limit(request, id):
    user_profile = UserProfile.objects.get(id=id)
    if request.method == 'POST':
        is_bussines = request.POST.get('is_bussines')
        is_maxsulot_boshkaruvi = request.POST.get('is_maxsulot_boshkaruvi')
        is_maxsulot_tahriri = request.POST.get('is_maxsulot_tahriri')
        is_taminotchi_qaytuv = request.POST.get('is_taminotchi_qaytuv')
        is_bugungi_sotuvlar = request.POST.get('is_bugungi_sotuvlar')
        is_maxsutlo_tahlili = request.POST.get('is_maxsutlo_tahlili')
        is_analiz_xarajatlar = request.POST.get('is_analiz_xarajatlar')
        is_ot_prixod = request.POST.get('is_ot_prixod')
        is_ot_tarix = request.POST.get('is_ot_tarix')
        is_hisobdan_chiqish = request.POST.get('is_hisobdan_chiqish')
        is_hisobdan_tarix = request.POST.get('is_hisobdan_tarix')
        is_xodim_kunlik = request.POST.get('is_xodim_kunlik')
        is_xodim_oylik = request.POST.get('is_xodim_oylik')
        is_xodim_mobile = request.POST.get('is_xodim_mobile')
        is_xodim_call_center = request.POST.get('is_xodim_call_center')
        is_balans_hisobi = request.POST.get('is_balans_hisobi')
        is_fin_hisoboti = request.POST.get('is_fin_hisoboti')
        is_buyurtmalar = request.POST.get('is_buyurtmalar')
        is_filial_boshkaruvi = request.POST.get('is_filial_boshkaruvi')
        is_kadrlar = request.POST.get('is_kadrlar')
        is_mijozlar_qarzdorligi = request.POST.get('is_mijozlar_qarzdorligi')
        is_mijozlar_tahlili = request.POST.get('is_mijozlar_tahlili')
        is_yetkazib_beruvchilar = request.POST.get('is_yetkazib_beruvchilar')
        is_ombor_boshkaruvi_ombor = request.POST.get('is_ombor_boshkaruvi_ombor')
        is_ombor_boshkaruvi_qabul = request.POST.get('is_ombor_boshkaruvi_qabul')
        is_ombor_boshkaruvi_ombordan_analiz = request.POST.get('is_ombor_boshkaruvi_ombordan_analiz')
        is_reyting_maxsulotlar = request.POST.get('is_reyting_maxsulotlar')
        is_reyting_mijozlar = request.POST.get('is_reyting_mijozlar')
        is_reyting_yetkazib_beruvchilar = request.POST.get('is_reyting_yetkazib_beruvchilar')
        is_kassa = request.POST.get('is_kassa')
        is_savdo = request.POST.get('is_savdo')
        is_b2b_savdo = request.POST.get('is_b2b_savdo')
        is_kassa_tasdiklanmagan = request.POST.get('is_kassa_tasdiklanmagan')
        is_qabul = request.POST.get('is_qabul')
        is_nds = request.POST.get('is_nds')
        is_kassa_tarixi = request.POST.get('is_kassa_tarixi')
        is_bugungi_amaliyotlar = request.POST.get('is_bugungi_amaliyotlar')

        is_reviziya = request.POST.get('is_reviziya')
        is_reviziya_tarixi = request.POST.get('is_reviziya_tarixi')
        is_turli_shaxs = request.POST.get('is_turli_shaxs')
        is_taminotchi_qaytuv_tarix = request.POST.get('is_taminotchi_qaytuv_tarix')
        is_filial_kassalar = request.POST.get('is_filial_kassalar')

        is_measurement_type = request.POST.get('is_measurement_type')
        is_price_type = request.POST.get('is_price_type')
        is_filial_list = request.POST.get('is_filial_list')
        is_valyuta = request.POST.get('is_valyuta')
        is_kassa_merge = request.POST.get('is_kassa_merge')
        is_kassa_new = request.POST.get('is_kassa_new')
        is_money_circulation = request.POST.get('is_money_circulation')

        user_profile.is_measurement_type=True if  is_measurement_type == 'on' else False
        user_profile.is_price_type=True if  is_price_type == 'on' else False
        user_profile.is_filial_list=True if  is_filial_list == 'on' else False
        user_profile.is_valyuta=True if  is_valyuta == 'on' else False
        user_profile.is_kassa_merge=True if  is_kassa_merge == 'on' else False
        user_profile.is_kassa_new=True if  is_kassa_new == 'on' else False
        user_profile.is_money_circulation=True if  is_money_circulation == 'on' else False

        user_profile.is_filial_kassalar=True if  is_filial_kassalar == 'on' else False
        user_profile.is_taminotchi_qaytuv_tarix=True if  is_taminotchi_qaytuv_tarix == 'on' else False
        user_profile.is_turli_shaxs=True if  is_turli_shaxs == 'on' else False
        user_profile.is_reviziya=True if  is_reviziya == 'on' else False
        user_profile.is_reviziya_tarixi=True if  is_reviziya_tarixi == 'on' else False

        user_profile.is_bugungi_amaliyotlar=True if  is_bugungi_amaliyotlar == 'on' else False
        user_profile.is_bussines=True if  is_bussines == 'on' else False
        user_profile.is_maxsulot_boshkaruvi=True if  is_maxsulot_boshkaruvi == 'on' else False
        user_profile.is_maxsulot_tahriri=True if  is_maxsulot_tahriri == 'on' else False
        user_profile.is_taminotchi_qaytuv=True if  is_taminotchi_qaytuv == 'on' else False
        user_profile.is_bugungi_sotuvlar=True if  is_bugungi_sotuvlar == 'on' else False
        user_profile.is_maxsutlo_tahlili=True if  is_maxsutlo_tahlili == 'on' else False
        user_profile.is_analiz_xarajatlar=True if  is_analiz_xarajatlar == 'on' else False
        user_profile.is_ot_prixod=True if  is_ot_prixod == 'on' else False
        user_profile.is_ot_tarix=True if  is_ot_tarix == 'on' else False
        user_profile.is_hisobdan_chiqish=True if  is_hisobdan_chiqish == 'on' else False
        user_profile.is_hisobdan_tarix=True if  is_hisobdan_tarix == 'on' else False
        user_profile.is_xodim_kunlik=True if  is_xodim_kunlik == 'on' else False
        user_profile.is_xodim_oylik=True if  is_xodim_oylik == 'on' else False
        user_profile.is_xodim_mobile=True if  is_xodim_mobile == 'on' else False
        user_profile.is_xodim_call_center=True if  is_xodim_call_center == 'on' else False
        user_profile.is_balans_hisobi=True if  is_balans_hisobi == 'on' else False
        user_profile.is_fin_hisoboti=True if  is_fin_hisoboti == 'on' else False
        user_profile.is_buyurtmalar=True if  is_buyurtmalar == 'on' else False
        user_profile.is_filial_boshkaruvi=True if  is_filial_boshkaruvi == 'on' else False
        user_profile.is_kadrlar=True if  is_kadrlar == 'on' else False
        user_profile.is_mijozlar_qarzdorligi=True if  is_mijozlar_qarzdorligi == 'on' else False
        user_profile.is_mijozlar_tahlili=True if  is_mijozlar_tahlili == 'on' else False
        user_profile.is_yetkazib_beruvchilar=True if  is_yetkazib_beruvchilar == 'on' else False
        user_profile.is_ombor_boshkaruvi_ombor=True if  is_ombor_boshkaruvi_ombor == 'on' else False
        user_profile.is_ombor_boshkaruvi_qabul=True if  is_ombor_boshkaruvi_qabul == 'on' else False
        user_profile.is_ombor_boshkaruvi_ombordan_analiz=True if  is_ombor_boshkaruvi_ombordan_analiz == 'on' else False
        user_profile.is_reyting_maxsulotlar=True if  is_reyting_maxsulotlar == 'on' else False
        user_profile.is_reyting_mijozlar=True if  is_reyting_mijozlar == 'on' else False
        user_profile.is_reyting_yetkazib_beruvchilar=True if  is_reyting_yetkazib_beruvchilar == 'on' else False
        user_profile.is_kassa=True if  is_kassa == 'on' else False
        user_profile.is_savdo=True if  is_savdo == 'on' else False
        user_profile.is_b2b_savdo=True if  is_b2b_savdo == 'on' else False
        user_profile.is_kassa_tasdiklanmagan=True if  is_kassa_tasdiklanmagan == 'on' else False
        user_profile.is_qabul=True if  is_qabul == 'on' else False
        user_profile.is_nds=True if  is_nds == 'on' else False
        user_profile.is_kassa_tarixi=True if  is_kassa_tarixi == 'on' else False 
        user_profile.save()
        return redirect('users_restrictions')
    context = {
        'use':user_profile,
    }
    return render(request, 'users_restrictions_limit.html', context)



def users_add(request):
    username = request.POST.get('username')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    password = request.POST.get('password')
    use = User.objects.create_superuser(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
    )
    UserProfile.objects.create(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
        user=use
    )
    return redirect(request.META['HTTP_REFERER'])

def users_change(request, id):
    user_profile = UserProfile.objects.get(id=id)
    
    username = request.POST.get('username')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    password = request.POST.get('password')
    if username:
        user_profile.username = username
    if first_name:
        user_profile.first_name = first_name
    if last_name:
        user_profile.last_name = last_name
    if password:
        user_profile = password
    user_profile.save()
    if user_profile.user:
        use = User.objects.get(id=user_profile.user.id)
        if username:
            use.username = username
        if first_name:
            use.first_name = first_name
        if last_name:
            use.last_name = last_name
        if password:
            use.set_password(password)
        use.save()
    return redirect(request.META['HTTP_REFERER'])

def users_delete(request, id):
    use = User.objects.get(id=id).delete()
    return redirect(request.META['HTTP_REFERER'])


def price_type(request):
    context = {
        'price':PriceType.objects.filter(is_activate=True),
    }
    return render(request, 'price_type.html', context)

def price_type_add(request):
    name = request.POST.get('name')
    code = request.POST.get('code')
    PriceType.objects.create(
        name=name,
        code=code,
    )
    return redirect(request.META['HTTP_REFERER'])


def price_type_edit(request, id):
    name = request.POST.get('name')
    code = request.POST.get('code')
    price = PriceType.objects.get(id=id)
    price.name=name
    price.code=code
    price.save()
    return redirect(request.META['HTTP_REFERER'])

def price_type_del(request, id):
    price = PriceType.objects.get(id=id)
    price.is_activate = False
    price.save()
    return redirect(request.META['HTTP_REFERER'])

from django.db.models import OuterRef, Subquery

def product_price_type(request, id):
    price_dollar_subquery = ProductPriceType.objects.filter(
        type_id=id,
        product=OuterRef('pk')
    ).values('price_dollar')[:1]

    price_som_subquery = ProductPriceType.objects.filter(
        type_id=id,
        product=OuterRef('pk')
    ).values('price')[:1]

    products = ProductFilial.objects.annotate(
        price_type_dollar=Subquery(price_dollar_subquery),
        price_type_som=Subquery(price_som_subquery)
    )
    context = {
        'product':products,
        'type_payment_id':id,
        # 'product':
    }
    return render(request, 'product_price_type.html', context)

def add_product_price_type(request):
    json_data = json.loads(request.body)
    for i in json_data:
        obj , created =  ProductPriceType.objects.get_or_create(
            type_id=i['id'],
            product_id=i['product_id'])
        obj.price = i['price_som']
        obj.price_dollar = i['price_dollar']
        obj.save()
    return redirect('price_type')


# def top_delivers(request):
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')
#     # seller_id = [int(i) for i in request.GET.getlist('seller')  if i != '']
#     # hudud = [int(i) for i in request.GET.getlist('hudud')  if i != '']
#     # type_country = [int(i) for i in request.GET.getlist('country')  if i != '']


#     orders = Shop.objects.all()
    
#     if start_date and end_date:
#         orders = orders.filter(date__gte=start_date, date__lte=end_date)
#     else:
#         orders = orders.filter(date__gte=datetime.now().date().replace(day=1))
    
#     # if hudud:
#     #     orders = orders.filter(debtor__teritory__in=hudud)
    
#     # if seller_id:
#     #     orders = orders.filter(saler_id__in=seller_id)
    
        
#     baskets = Cart.objects.filter(shop__in=orders)

#     # if type_country:
#     #     baskets = baskets.filter(product__product__type_country__in=type_country)

    
    

#     debtors = Debtor.objects.filter(debtor_shops__in=orders).distinct()
    
#     data = []

#     for i in debtors:
#         data.append({
#             'debtor': i,
#             'order_count': orders.filter(debtor=i).count(),
#             'total_price': baskets.filter(shop__debtor=i).aggregate(foo=Coalesce(Sum('total'), float(0), output_field=FloatField()))['foo'],
#             'foyda': baskets.filter(shop__debtor=i).aggregate(foo=Coalesce(Sum(F('total') - (F('quantity') * F('bring_price'))), float(0), output_field=FloatField()))['foo'],
#             'total_count': baskets.filter(shop__debtor=i).aggregate(foo=Coalesce(Sum('quantity'), float(0), output_field=FloatField()))['foo'],
#         })
        
    
#     totals = {
#         'order_count': orders.count(),
#         'total_price': baskets.aggregate(foo=Coalesce(Sum('total'), float(0), output_field=FloatField()))['foo'],
#         'foyda': baskets.aggregate(foo=Coalesce(Sum(F('total') - (F('quantity') * F('bring_price'))), float(0), output_field=FloatField()))['foo'],
#         'total_count': baskets.aggregate(foo=Coalesce(Sum('quantity'), float(0), output_field=FloatField()))['foo'],
#     }

#     filters = {
#         'start_date': start_date,
#         'end_date': end_date,
#         'seller': seller_id,
#         'hudud': hudud,
#     }

#     context = {
#         'totals': totals,
#         'filters': filters,
#         'data': data,
#         'viloyatlar': Teritory.objects.all(),
#         # 'countries': countries,
#         # 'products': Store.objects.all(),
#         'sellers': UserProfile.objects.filter(staff=3).distinct()
#     }

#     return render(request, 'top_debtors.html', context)




def top_delivers(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    # seller_id = [int(i) for i in request.GET.getlist('seller')  if i != '']
    # hudud = [int(i) for i in request.GET.getlist('hudud')  if i != '']
    # type_country = [int(i) for i in request.GET.getlist('country')  if i != '']


    orders = Recieve.objects.all()
    
    if start_date and end_date:
        orders = orders.filter(date__gte=start_date, date__lte=end_date)
    else:
        orders = orders.filter(date__gte=datetime.now().date().replace(day=1))
    
    # if hudud:
    #     orders = orders.filter(debtor__teritory__in=hudud)
    
    # if seller_id:
    #     orders = orders.filter(saler_id__in=seller_id)
    
        
    baskets = RecieveItem.objects.filter(recieve__in=orders)

    # if type_country:
    #     baskets = baskets.filter(product__product__type_country__in=type_country)

    
    delivers = Deliver.objects.all()

    products = ProductFilial.objects.filter(product_recieves__in=baskets).distinct()
    
    data = []

    for i in delivers:
        data.append({
            'deliver': i,
            'order_count': orders.filter(deliver=i).count(),
            'total_price': baskets.filter(recieve__deliver=i).aggregate(foo=Coalesce(Sum(F('quantity') * F('som')), float(0), output_field=FloatField()))['foo'],
            'total_count': baskets.filter(recieve__deliver=i).aggregate(foo=Coalesce(Sum('quantity'), float(0), output_field=FloatField()))['foo'],
        })
        
    
    totals = {
        'order_count': orders.count(),
        'total_price': baskets.aggregate(foo=Coalesce(Sum(F('quantity') * F('som')), float(0), output_field=FloatField()))['foo'],
        'total_count': baskets.aggregate(foo=Coalesce(Sum('quantity'), float(0), output_field=FloatField()))['foo'],
    }

    filters = {
        'start_date': start_date,
        'end_date': end_date,
        # 'seller': seller_id,
        # 'hudud': hudud,
    }

    context = {
        'totals': totals,
        'filters': filters,
        'data': data,
        'viloyatlar': Teritory.objects.all(),
        # 'countries': countries,
        # 'products': Store.objects.all(),
        'sellers': UserProfile.objects.filter(staff=3)
    }

    return render(request, 'top_delivers.html', context)



def create_order(request):
    price_types = PriceType.objects.all()
    products = ProductFilial.objects.all()
    customers = Debtor.objects.all()
    call_center = UserProfile.objects.filter(staff=6)

    context = {
       'price_types': price_types,
       'products': products,
       'call_center': call_center,
       'customers': customers,
       'dollar_kurs': Course.objects.last().som if Course.objects.last() else 0
    }

    return render(request, 'create_order.html', context)

def finish_order(request, id):
    shop = Shop.objects.get(id=id)
    shop.is_finished = True
    shop.save()
    return redirect(request.META['HTTP_REFERER'])

def refresh_debtor_debt(request, id):
    debtor = Debtor.objects.get(id=id)
    debtor.refresh_debt()
    # shop.save()
    return redirect(request.META['HTTP_REFERER'])


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_order_ajax(request):
    if request.method == 'POST':
        main_valuta = request.POST.get('main_valuta')
        order_id = request.POST.get('order_id')
        customer = request.POST.get('customer')
        kurs = request.POST.get('kurs')
        payment_date = request.POST.get('payment_date')
        call_center = request.POST.get('call_center')

        naqd_som = float(request.POST.get('naqd_som', 0))
        naqd_dollar = float(request.POST.get('naqd_dollar', 0))
        plastik = float(request.POST.get('plastik', 0))
        click = float(request.POST.get('click', 0))

        nasiya_som = float(request.POST.get('nasiya_som', 0))
        nasiya_dollar = float(request.POST.get('nasiya_dollar', 0))


        if not order_id:
            if customer and payment_date and call_center:
                call_center = UserProfile.objects.get(id=call_center)
                order = Shop.objects.create(
                    debtor_id=customer,
                    kurs=kurs,
                    debt_return=payment_date,
                    call_center=call_center.first_name,
                    filial=Filial.objects.last(),
                    is_som=True if main_valuta == 'som' else False,
                    is_dollar=True if main_valuta == 'dollar' else False,
                )
                return JsonResponse({'success': True, 'order_id': order.id})
            return JsonResponse({'success': False, 'message': 'Ma\'lumotlar yetarli emas'})
        else:
            order = Shop.objects.get(id=order_id)
            order.debtor_id = customer
            order.kurs = kurs
            order.debt_return = payment_date
            order.call_center = call_center
            order.is_som=True if main_valuta == 'som' else False
            order.is_dollar=True if main_valuta == 'dollar' else False

            order.naqd_som = naqd_som
            order.naqd_dollar = naqd_dollar
            order.plastik = plastik
            order.click = click
            order.nasiya_som = nasiya_som
            order.nasiya_dollar = nasiya_dollar

            order.save()
            return JsonResponse({'success': True, 'order_id': order.id})
            # return JsonResponse({'success': False, 'message': 'Ma\'lumotlar yetarli emas'})
    return JsonResponse({'success': False, 'message': 'POST so\'rovi emas'})

@csrf_exempt
def order_detail_ajax(request, order_id):
    action = request.POST.get('action')  # Qo'shish, o'chirish yoki edit qilish
    # order_id = request.POST.get('order_id')  # Order ID
    product_id = request.POST.get('product_id')  # Maxsulot ID
    cart_id = request.POST.get('cart_id')  # Maxsulot ID
    quantity = request.POST.get('quantity')  # Miqdor
    agreed_price = request.POST.get('agreed_price')  
    product_price = request.POST.get('product_price')  
    shop = Shop.objects.get(id=order_id)
    if action == 'add':
        product = ProductFilial.objects.get(id=product_id)

        if product.quantity < float(quantity):
            return JsonResponse({'success': False, 'message': f'Qoldiq yetarli emas, {product.quantity}'})
        cart_item = Cart.objects.create(
            shop=shop,
            product=product,
            quantity=quantity,
            price=agreed_price,
            price_without_skidka = product_price,
            total=int(quantity) * int(agreed_price)
        )
        return JsonResponse({'success': True, 'message': 'Maxsulot qo\'shildi', 'cart_id': cart_item.id})
    
    elif action == 'edit':
        cart_item = Cart.objects.get(id=cart_id)
        product = cart_item.product
        product.quantity += cart_item.quantity
        product.quantity -= int(quantity)
        # product.quantity = -2

        if product.quantity < 0:
            return JsonResponse({'success': False, 'message': f'Qoldiq yetarli emas, {product.quantity}'})
        cart_item.quantity = quantity
        cart_item.total = int(quantity) * cart_item.price
        cart_item.save()
        return JsonResponse({'success': True, 'message': f'Maxsulot tahrirlandi'})
    
    elif action == 'delete':
        # Cartdagi maxsulotni o'chirish
        Cart.objects.filter(id=cart_id).delete()
        return JsonResponse({'success': True, 'message': 'Maxsulot o\'chirildi'})
    
    # else:
    #     return JsonResponse({'success': False, 'message': 'Noto\'g\'ri amal'})


    price_types = PriceType.objects.all()
    products = ProductFilial.objects.all()
    customers = Debtor.objects.all()
    call_center = UserProfile.objects.filter(staff=6)
    carts = Cart.objects.filter(shop=shop)

    context = {
       'price_types': price_types,
       'products': products,
       'call_center': call_center,
       'customers': customers,
       'dollar_kurs': Course.objects.last().som if Course.objects.last() else 0,
       'order': shop,
       'carts': carts,
       'order_id_check':order_id,
    }
    return render(request, 'create_order.html', context)
from django.core.serializers.json import DjangoJSONEncoder

def create_check(request, order_id):
    shop = Shop.objects.get(id=order_id)
    cart = Cart.objects.filter(shop=shop)
    data = {
        'chek':order_id,
        'seller':shop.saler.first_name,
        'date':shop.date.strftime('%Y-%m-%d %H:%M:%S'),
        'valyuta':shop.valyuta.name if shop.valyuta else '',
        'items':[
                {"name": cart.product.name, "quantity": cart.quantity, "price": cart.price, "total": cart.total}
            for cart in cart
        ],
        'summa': shop.total_price,
    }
    return JsonResponse(data, encoder=DjangoJSONEncoder)

def shop_nakladnoy(request, order_id):
    shop = Shop.objects.get(id=order_id)
    cart = Cart.objects.filter(shop=shop)
    data = {
        'chek':order_id,
        'seller':shop.saler,
        'date_time':shop.date,
        'customer':shop.debtor.fio,
        'valyuta':shop.valyuta.name if shop.valyuta else '',
        'customer_phone':shop.debtor.phone1,
        'date':shop.date.strftime('%Y-%m-%d %H:%M:%S'),
        'items':[
                {
                    "name": cart.product.name, 
                    "quantity": cart.quantity, 
                    "price": cart.price, 
                    "total": cart.total,
                    'img':cart.product.image,
                    'nds_price':(cart.price / 100 * shop.nds_count) + cart.price,
                    'nds_total':(cart.total / 100 * shop.nds_count) + cart.total,
                }
            for cart in cart
        ],
        'som': shop.naqd_som,
        'dollar': shop.naqd_dollar,
        'skidka_dollar': shop.skidka_dollar,
        'skidka_som': shop.skidka_som,

    }
    summa = cart.aggregate(foo=Coalesce(Sum('total'), float(0), output_field=FloatField()))['foo']
    total = {
        'summa':summa,
        'summa_nds':(summa / 100 * shop.nds_count) + summa,
        'quantity':cart.aggregate(foo=Coalesce(Sum('quantity'), float(0), output_field=FloatField()))['foo'],
        'price':cart.aggregate(foo=Coalesce(Sum('price'), float(0), output_field=FloatField()))['foo'],
    }
    context = {
        'data':data,
        'total':total
    }
    return render(request, 'shop_nakladnoy.html', context)

def check_price(request):
    price_type = request.GET.get('type')
    product = request.GET.get('product')

    if price_type and product:
        price = ProductPriceType.objects.filter(type_id=price_type, product_id=product).last()
        if price:
            return JsonResponse({
                "price": price.price
            })
        
    if product and not price_type:
        return JsonResponse({
            "price": ProductFilial.objects.get(id=product).sotish_som
        })

    return JsonResponse({
        "price": 0
    })

from django.core.paginator import Paginator

def b2c_shop_view(request):
    price_types = PriceType.objects.all()
    products = ProductFilial.objects.all()
    customers = Debtor.objects.all()
    call_center = UserProfile.objects.filter(staff=6)

    context = {
       'price_types': price_types,
       'products': products,
       'call_center': call_center,
       'customers': customers,
       'dollar_kurs': Course.objects.last().som if Course.objects.last() else 0,
       'valyuta':Valyuta.objects.all(),
       'filial':Filial.objects.filter(is_activate=True),
    }
    return render(request, 'b2c_shop.html', context)

def b2c_shop_add(request):
    shop = Shop.objects.create(
        valyuta_id=request.POST.get('valyuta'),
        type_price_id=request.POST.get('type_price'),
        debtor_id=request.POST.get('debtor'),
        saler_id=request.POST.get('call_center'),
        debt_return=request.POST.get('debt_return'),
        filial_id=request.POST.get('filial'),
    )
    return redirect('b2c_shop_detail', shop.id)

def b2c_shop_detail(request, id):
    shop = Shop.objects.get(id=id)
    price_types = PriceType.objects.all()
    products = ProductFilial.objects.all()
    customers = Debtor.objects.all()
    call_center = UserProfile.objects.filter(staff=6)
    cart = Cart.objects.filter(shop=shop)
    totals = {
        'quantity':cart.aggregate(all=Coalesce(Sum('quantity'), 0, output_field=IntegerField()))['all'],
        'total':cart.aggregate(all=Coalesce(Sum('total'), 0, output_field=IntegerField()))['all'],
    }
    context = {
       'shop':shop,
       'cart':cart,
       'totals':totals,
       'price_types': price_types,
       'products': products,
       'call_center': call_center,
       'customers': customers,
       'dollar_kurs': Course.objects.last().som if Course.objects.last() else 0,
       'valyuta':Valyuta.objects.all(),
       'filial':Filial.objects.filter(is_activate=True),
    }
    return render(request, 'b2c_shop_detail.html', context)

@csrf_exempt
def b2c_shop_cart_add(request, id):
    product_id = request.POST.get('product_id')  
    quantity = float(request.POST.get('quantity'))  
    agreed_price = request.POST.get('agreed_price')  
    product_price = request.POST.get('product_price')  
    shop = Shop.objects.get(id=id)
    product = ProductFilial.objects.get(id=product_id)
    if product.quantity < float(quantity):
        return JsonResponse({'success': False, 'message': f'Qoldiq yetarli emas, {product.quantity}'})
    cart_item = Cart.objects.create(
        shop=shop,
        product=product,
        quantity=quantity,
        price=float(agreed_price),
        price_without_skidka = product_price,
        total=float(quantity) * float(agreed_price)
    )
    product.quantity -= quantity
    product.save()
    return JsonResponse({'success': True, 'message': 'Maxsulot qo\'shildi', 'cart_id': cart_item.id})

@csrf_exempt
def b2c_shop_cart_edit(request, id):
    quantity = request.POST.get('quantity')  
    cart_item = Cart.objects.get(id=id)
    product = cart_item.product
    product.quantity += cart_item.quantity
    product.quantity -= float(quantity)
    if product.quantity < 0:
        return JsonResponse({'success': False, 'message': f'Qoldiq yetarli emas, {product.quantity}'})
    cart_item.quantity = quantity
    cart_item.total = float(quantity) * cart_item.price
    cart_item.save()
    product.save()
    print(quantity)
    return JsonResponse({'success': True, 'message': 'Maxsulot ozgartirildi'})



@csrf_exempt
def b2c_shop_cart_del(request, id):
    cart = Cart.objects.get(id=id)
    product = cart.product
    product.quantity += cart.quantity
    product.save()
    cart.delete()
    return JsonResponse({'success': True, 'message': 'Maxsulot o\'chirildi'})

@csrf_exempt
def b2c_shop_finish(request, id):
    shop = Shop.objects.get(id=id)
    summa = request.POST.get('summa')
    shop.is_finished = True
    PayHistory.objects.create(
        shop=shop,
        debtor=shop.debtor,
        filial=shop.filial,
        valyuta=shop.valyuta,
        summa=summa,
    )
    debtor = Debtor.objects.get(id=shop.debtor.id)
    debtor.refresh_debt()
    shop.save()
    return JsonResponse({'success': True, 'message': 'Yakunlandi'})


def today_sales(request):
    today = datetime.now().date()
    cart = Cart.objects.all()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    client = request.GET.getlist('client')
    deliver = request.GET.getlist('deliver')
    search = request.GET.get('search')
    filters = {
        start_date: '',
        end_date: '',
    }


    if start_date and end_date:
        cart = cart.filter(shop__date__range=(start_date, end_date))
        filters['start_date'] = start_date
        filters['end_date'] = end_date
    else:
        cart = cart.filter(shop__date=today)
        filters['start_date'] = today.strftime('%Y-%m-%d')
        filters['end_date'] = today.strftime('%Y-%m-%d')


    if search:
        cart = cart.filter(product__name__icontains=search)

    if deliver:
        cart = cart.filter(product__deliver1__id__in=deliver)

    if client:
        cart = cart.filter(shop__debtor_id__in=client)

    paginator_cart = Paginator(cart, 50)
    page_number = request.GET.get('page')
    page_cart = paginator_cart.get_page(page_number)

    totals = {
        'total_price': cart.aggregate(Sum('price')).get('price__sum', 0),
        'total_quantity': cart.aggregate(Sum('quantity')).get('quantity__sum', 0),
        'total': cart.aggregate(Sum('total')).get('total__sum', 0),
    }
    context = {
        'totals':totals,
        'filters':filters,
        'today': today,
        'cart': page_cart,
        'deliver':Deliver.objects.all(),
        'client':Debtor.objects.all(),
    }
    return render(request, 'today_sales.html', context)


def analysis_costs(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    chiqim = Chiqim.objects.filter(qayerga__isnull=False)
    chiqim_turi = ChiqimTuri.objects.all()
    today = datetime.now().date()

    filters = {
        start_date: '',
        end_date: '',
    }
    if start_date and end_date:
        chiqim = chiqim.filter(qachon__date__range=(start_date, end_date))
        filters['start_date'] = start_date
        filters['end_date'] = end_date
    else:
        first_month = datetime.now().replace(day=1)
        chiqim = chiqim.filter(qachon__date__range=(first_month , today))
        filters['start_date'] = first_month.strftime('%Y-%m-%d')
        filters['end_date'] = today.strftime('%Y-%m-%d')

    data = []


    summa_total = {
        'sum': chiqim.aggregate(Sum('qancha_som')).get('qancha_som__sum') or 0,
        'dollar': chiqim.aggregate(Sum('qancha_dol')).get('qancha_dol__sum') or 0,
        'plastik': chiqim.aggregate(Sum('plastik')).get('plastik__sum') or 0,
        'hisob_raqamdan': chiqim.aggregate(Sum('qancha_hisob_raqamdan')).get('qancha_hisob_raqamdan__sum') or 0,
    }

    data = []
    for i in chiqim_turi:
        filter_chiqim = chiqim.filter(qayerga=i)
        
        sum_qancha_som = filter_chiqim.aggregate(Sum('qancha_som')).get('qancha_som__sum') or 0
        sum_qancha_dol = filter_chiqim.aggregate(Sum('qancha_dol')).get('qancha_dol__sum') or 0
        sum_plastik = filter_chiqim.aggregate(Sum('plastik')).get('plastik__sum') or 0
        sum_qancha_hisob = filter_chiqim.aggregate(Sum('qancha_hisob_raqamdan')).get('qancha_hisob_raqamdan__sum') or 0

        dt = {
            'name': i.nomi,
            'sum': sum_qancha_som,
            'percent_sum': round((sum_qancha_som / summa_total['sum']) * 100, 2) if summa_total['sum'] else 0,

            'dollar': sum_qancha_dol,
            'percent_dollar': round((sum_qancha_dol / summa_total['dollar']) * 100, 2) if summa_total['dollar'] else 0,

            'plastik': sum_plastik,
            'percent_plastik': round((sum_plastik / summa_total['plastik']) * 100, 2) if summa_total['plastik'] else 0,

            'hisob_raqamdan': sum_qancha_hisob,
            'percent_hisob_raqamdan': round((sum_qancha_hisob / summa_total['hisob_raqamdan']) * 100, 2) if summa_total['hisob_raqamdan'] else 0,
        }

        data.append(dt)


    

    context = {
        'data':data,
        'summa_total':summa_total,
        'filters': filters,
        'today': today,
       
    }
    return render(request, 'analysis_costs.html', context)



def tovar_prixod(request):
    
    context = {

    }
    context['ombor'] = 'active'
    context['ombor_t'] = 'true'
    context['recieves'] = Recieve.objects.filter(status__in=[0, 1], is_prexoded=True).order_by('-id')
    context['recieveitems'] = RecieveItem.objects.filter(recieve__is_prexoded=True).order_by('-id')[:1000]
    context['dollar_kurs'] = Course.objects.last().som
    context['products'] = ProductFilial.objects.all()
    context['groups'] = Groups.objects.all()
    context['delivers'] = Deliver.objects.all()

    context['measurements'] = [{
        "id": i[0],
        "name": i[1],
    } for i in ProductFilial.measure]
    max_barcode = (
        ProductFilial.objects
        .annotate(barcode_int=Cast('barcode', IntegerField()))
        .aggregate(Max('barcode_int'))['barcode_int__max']
    )
    new_barcode = max_barcode+1 if max_barcode else 1

    context['new_barcode'] = new_barcode


    active_id = request.GET.get('active')
    if active_id and Recieve.objects.filter(id=active_id):
        context['active_one'] = Recieve.objects.get(id=active_id)

    return render(request, 'tovar_prixod.html', context)


def add_recieve_perexoded(request):
    name = request.POST.get('name', '')
    obj = Recieve.objects.create(name=name, is_prexoded=True)
    page = request.META['HTTP_REFERER']
    url_parts = urlparse(page)
    query = dict(parse_qsl(url_parts.query))
    query['active'] = obj.id 
    redirect_url = urlunparse(url_parts._replace(query=urlencode(query)))
    return redirect(redirect_url)



def tovar_prixod_tarix(request):
    recive = Recieve.objects.filter(is_prexoded=True)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    today = datetime.now().date()
    filters = {
        'start_date':'',
        'end_date':'',
    }
    if start_date and end_date:
        recive = recive.filter(date__date__range=(start_date, end_date))
        filters['start_date'] = start_date
        filters['end_date'] = end_date
    else:
        first_month = datetime.now().replace(day=1)
        recive = recive.filter(date__date__range=(first_month, today))
        filters['start_date'] = first_month.strftime('%Y-%m-%d')
        filters['end_date'] = today.strftime('%Y-%m-%d')

    summa_total = {
        'som':recive.aggregate(Sum('som')).get('som__sum') or 0,
        'sotish_som':recive.aggregate(Sum('sum_sotish_som')).get('sum_sotish_som__sum') or 0,
        'dollar':recive.aggregate(Sum('dollar')).get('dollar__sum') or 0,
        'sotish_dollar':recive.aggregate(Sum('sum_sotish_som')).get('sum_sotish_som__sum') or 0,
        'farq_dollar':recive.aggregate(Sum('farq_dollar')).get('farq_dollar__sum') or 0,
        'farq_som':recive.aggregate(Sum('farq_som')).get('farq_som__sum') or 0,
    }
    context = {
        'recive':recive,
        'filters':filters,
        'summa_total':summa_total
    }
    return render(request, 'tovar_prixod_tarix.html', context)


def tovar_prixod_tarix_detail(request, id):
    recive = RecieveItem.objects.filter(recieve_id=id)
    summa_total = {
        'som':recive.aggregate(Sum('som')).get('som__sum') or 0,
        'sotish_som':recive.aggregate(Sum('sotish_som')).get('sotish_som__sum') or 0,
        'dollar':recive.aggregate(Sum('dollar')).get('dollar__sum') or 0,
        'sotish_dollar':recive.aggregate(Sum('sotish_dollar')).get('sotish_dollar__sum') or 0,
        'quantity':recive.aggregate(Sum('quantity')).get('quantity__sum') or 0,
        'old_quantity':recive.aggregate(Sum('old_quantity')).get('old_quantity__sum') or 0,
        'old_sotish_som':recive.aggregate(Sum('old_sotish_som')).get('old_sotish_som__sum') or 0,
    }
    context = {
        'item':recive,
        'summa_total':summa_total
    }
    return render(request, 'tovar_prixod_tarix_detail.html', context)



def money_circulation(request):
    money = MoneyCirculation.objects.filter(is_delete=False)
    context = {
        'money':money,
        'chiqim_turi':ChiqimTuri.objects.all()
    }
    return render(request, 'fin/money_circulation.html', context)


def money_circulation_add(request):
    name = request.POST.get('name', '')
    manba = request.POST.get('manba')
    sub_manba = request.POST.get('sub_manba')
    xarajat_turi = request.POST.get('xarajat_turi')
    chiqim_turi = request.POST.get('chiqim_turi')
    manba_turi = request.POST.get('manba_turi')
    MoneyCirculation.objects.create(
        name=name,
        manba=manba,
        sub_manba=sub_manba,
        # xarajat_turi_id=xarajat_turi,
        chiqim_turi_id=chiqim_turi,
        manba_turi=True if manba_turi == 'on' else False, 
        )
    return redirect(request.META['HTTP_REFERER'])


def money_circulation_edit(request, id):
    money = MoneyCirculation.objects.get(id=id)
    name = request.POST.get('name', '')

    manba = request.POST.get('manba')
    sub_manba = request.POST.get('sub_manba')
    xarajat_turi = request.POST.get('xarajat_turi')
    chiqim_turi = request.POST.get('chiqim_turi')
    manba_turi = request.POST.get('manba_turi')

    money.name = name
    money.manba = manba
    money.sub_manba = sub_manba
    # money.xarajat_turi_id = xarajat_turi
    money.chiqim_turi_id = chiqim_turi
    money.manba_turi = True if manba_turi == 'on' else False
    money.save()
    return redirect(request.META['HTTP_REFERER'])

def money_circulation_delete(request, id):
    money = MoneyCirculation.objects.get(id=id)
    money.is_delete = True
    money.save()
    return redirect(request.META['HTTP_REFERER'])


def write_off(request):
    write_off = WriteOff.objects.filter(is_activate=True)
    today = datetime.now()

    totals = {

    }
    
    context = {
        'today':today,
        'write_off':write_off,
        'ombor':Filial.objects.all(),
        'valyutas':Valyuta.objects.all(),
        'money': MoneyCirculation.objects.filter(is_delete=False),
        'products': ProductFilial.objects.all(),
        'write_off_item': WriteOffItem.objects.all(),
        'valyuta': Valyuta.objects.all(),
        'active_one':'',
    }
    active_id = request.GET.get('active')
    if active_id and WriteOff.objects.filter(id=active_id):
        context['active_one'] = WriteOff.objects.get(id=active_id)
        context['active_id'] = active_id

    return render(request, 'write_off.html', context)

# def write_off(request):
#     write_off = WriteOff.objects.filter(is_activate=True)
#     today = datetime.now()
#     write_off_item = WriteOffItem.objects.all()

#     # price_totals = []
#     # total_price_totals = []

#     # for i in write_off_item:
#     #     price_totals.append()
#     # for valyuta in valyutas:
#     #     total = 0
#     #     for item in write_off_item:
#     #         price_obj = item.prices.filter(valyuta=valyuta).last()
#     #         if price_obj:
#     #             total += price_obj.price * item.quantity
#     #     totals.append({
#     #         'valyuta': valyuta,
#     #         'total': total
#     #     })

    
#     context = {
#         'today':today,
#         'write_off':write_off,
#         'ombor':Filial.objects.all(),
#         'valyutas':Valyuta.objects.all(),
#         'money': MoneyCirculation.objects.filter(is_delete=False),
#         'products': ProductFilial.objects.all(),
#         'write_off_item': WriteOffItem.objects.all(),
#         'active_one':'',
#     }
#     active_id = request.GET.get('active')
#     if active_id and WriteOff.objects.filter(id=active_id):
#         context['active_one'] = WriteOff.objects.get(id=active_id)
#         context['active_id'] = active_id

#     return render(request, 'write_off.html', context)

def write_off_add(request):
    number = request.POST.get('number')
    date_time = request.POST.get('date_time')
    kurs =Course.objects.last()
    money_type = request.POST.get('money_type')
    product_filial = request.POST.get('product_filial')
    izoh = request.POST.get('izoh')
    valyuta = request.POST.get('valyuta')
    WriteOff.objects.create(
        number=number,
        date_time=date_time,
        kurs=kurs.som if kurs else 0,
        money_type_id=money_type,
        product_filial_id=product_filial,
        izoh=izoh,
        valyuta_id=valyuta,
    )
    return redirect(request.META['HTTP_REFERER'])

def write_off_item_add(request):
    write_off_id = request.POST.get('write_off_id')
    product_filial = request.POST.get('product_filial')
    quantity = float(request.POST.get('quantity').replace(',','.'))
    WriteOffItem.objects.create(
        write_off_id=write_off_id,
        product_id=product_filial,
        quantity=quantity,
    )
    pr = ProductFilial.objects.get(id=product_filial)
    # if pr.quantity >= quantity:
    pr.quantity -= float(quantity)
    pr.save()
    return redirect(request.META['HTTP_REFERER'])

def write_off_item_delete(request, id):
    WriteOffItem.objects.get(id=id).delete()
    return redirect(request.META['HTTP_REFERER'])

def write_off_delete(request, id):
    WriteOff.objects.get(id=id).delete()
    return redirect('write_off')

def write_off_item_edit(request, id):
    quantity = float(request.POST.get('quantity').replace(',', ''))
    item =  WriteOffItem.objects.get(id=id)
    sum = quantity - item.quantity 
    pr = ProductFilial.objects.get(id=item.product.id)
    pr.quantity -= float(sum)
    pr.save()
    item.quantity = quantity
    item.save()
    return redirect(request.META['HTTP_REFERER'])

def write_off_tarix(request):
    off = WriteOff.objects.filter(is_activate=False)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    today = datetime.now().date()
    filters = {
        'start_date':'',
        'end_date':'',
    }
    if start_date and end_date:
        off = off.filter(date_time__date__range=(start_date, end_date))
        filters['start_date'] = start_date
        filters['end_date'] = end_date
    else:
        first_month = datetime.now().replace(day=1)
        off = off.filter(date_time__date__range=(first_month, today))
        filters['start_date'] = first_month.strftime('%Y-%m-%d')
        filters['end_date'] = today.strftime('%Y-%m-%d')

    context = {
        'recive':off,
        'filters':filters,
    }
    return render(request, 'write_off_tarix.html', context)

def write_off_item_detail(request, id):
    item = WriteOffItem.objects.filter(write_off_id=id)
    context = {
        'item':item,
        'total_quantity':item.aggregate(all=Coalesce(Sum('quantity'), 0, output_field=IntegerField()))['all'],
        'total_som':sum(i.summa_total_som for i in item),
        'total_dollar':sum(i.summa_total_dollar for i in item),
    }
    return render(request, 'write_off_item_detail.html', context)

def write_off_exit(request, id):
    r = WriteOff.objects.get(id=id)
    r.is_activate = False
    r.save()
    return redirect('write_off_tarix')

def deliver_return(request):
    return_product = ReturnProductToDeliver.objects.filter(is_activate=True)
    today = datetime.now()
    
    context = {
        'today':today,
        'return_product':return_product,
        'filial':Filial.objects.filter(is_activate=True),
        'deliver': Deliver.objects.all(),
        'valyuta': Valyuta.objects.all(),
        'products': ProductFilial.objects.all(),
        'returen_item': ReturnProductToDeliverItem.objects.all(),
    }
    active_id = request.GET.get('active')
    if active_id and ReturnProductToDeliver.objects.filter(id=active_id):
        context['active_one'] = ReturnProductToDeliver.objects.get(id=active_id)
        context['active_id'] = active_id
  
    return render(request, 'deliver_return.html', context)

def deliver_return_add(request):
    deliver = request.POST.get('deliver') 
    filial = request.POST.get('filial')
    # som = request.POST.get('som')
    # dollar = request.POST.get('dollar')
    date = request.POST.get('date')
    # valyuta = request.POST.get('valyuta')
    kurs =Course.objects.last()

    ReturnProductToDeliver.objects.create(
        deliver_id=deliver,
        filial_id=filial,
        # som=som,
        # dollar=dollar,
        date=date,
        # valyuta_id=valyuta,
        kurs=kurs.som if kurs else 0,

    )
    return redirect(request.META['HTTP_REFERER'])

def deliver_return_item_add(request):
    returnproduct = request.POST.get('returnproduct')
    product = request.POST.get('product_filial')
    quantity = int(request.POST.get('quantity'))
    som = int(request.POST.get('som') or 0)
    dollar = int(request.POST.get('dollar') or 0)
    ReturnProductToDeliverItem.objects.create(
        returnproduct_id=returnproduct,
        product_id=product,
        summa=summa,
        # dollar=dollar,
        quantity=quantity,
        valyuta_id=valyuta
    )
    pr = ProductFilial.objects.get(id=product)
    pr.quantity -= int(quantity)
    pr.save()
    return redirect(request.META['HTTP_REFERER'])

def deliver_return_del(request, id):
    ReturnProductToDeliver.objects.get(id=id).delete()
    return redirect(request.META['HTTP_REFERER'])

def deliver_return_item_del(request, id):
    ReturnProductToDeliverItem.objects.get(id=id).delete()
    return redirect(request.META['HTTP_REFERER'])

def deliver_return_item_edit(request, id):
    item = ReturnProductToDeliverItem.objects.get(id=id)
    quantity = int(request.POST.get('quantity'))
    som = int(request.POST.get('som'))
    dollar = int(request.POST.get('dollar'))
    sum = quantity - item.quantity 
    pr = ProductFilial.objects.get(id=item.product.id)
    pr.quantity -= int(sum)
    pr.save()
    item.quantity = quantity
    item.summa = summa
    item.valyuta_id = valyuta
    item.save()
    return redirect(request.META['HTTP_REFERER'])

def deliver_return_tarix(request):
    off = ReturnProductToDeliver.objects.filter(is_activate=False)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    today = datetime.now().date()
    filters = {
        'start_date':'',
        'end_date':'',
    }
    if start_date and end_date:
        off = off.filter(date_time__date__range=(start_date, end_date))
        filters['start_date'] = start_date
        filters['end_date'] = end_date
    else:
        first_month = datetime.now().replace(day=1)
        off = off.filter(date__date__range=(first_month, today))
        filters['start_date'] = first_month.strftime('%Y-%m-%d')
        filters['end_date'] = today.strftime('%Y-%m-%d')

    context = {
        'recive':off,
        'filters':filters,
    }
    return render(request, 'deliver_return_tarix.html', context)

def deliver_return_item_detail(request, id):
    item = ReturnProductToDeliverItem.objects.filter(returnproduct_id=id)
    context = {
        'item':item,
        'total_quantity':item.aggregate(all=Coalesce(Sum('quantity'), 0, output_field=IntegerField()))['all'],
        'total_dollar':item.aggregate(all=Coalesce(Sum(F('quantity') * F('dollar')), 0, output_field=IntegerField()))['all'],
        'total_som':item.aggregate(all=Coalesce(Sum(F('quantity') * F('som')), 0, output_field=IntegerField()))['all'],
    }
    return render(request, 'deliver_return_item_detail.html', context)

def deliver_return_exit(request, id):
    r = ReturnProductToDeliver.objects.get(id=id)
    r.is_activate = False
    r.save()
    r.deliver.refresh_debt()
    return redirect(request.META['HTTP_REFERER'])


import time

def fin_report(request):
    context = {
    }
    return render(request, 'fin_report.html', context)

def kassa_fin(request):
    pay = (
        PayHistory.objects
        .select_related('debtor', 'money_circulation')
        .only('debtor__fio', 'money_circulation__name')
    )
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        pay = pay.filter(date__date__range=(start_date, end_date))

    filters = { 
        'start_date':start_date,
        'end_date':end_date,
    }
    paginator_pay = Paginator(pay, 100)
    page_number = request.GET.get('page')
    page_pay = paginator_pay.get_page(page_number)
    context = {
        'pay':page_pay,
        'filters':filters,
    }
    return render(request, 'fin/kassa_fin.html', context)


def exel_convert_kassa_fin(request):
    pay_qs = (
        PayHistory.objects
        .select_related('debtor', 'money_circulation')
        .only('debtor__fio', 'money_circulation__name', 'date', 'currency', 'comment')
    )
    
    pay_data = []
    for pay in pay_qs:
        pay_data.append({
            'date': pay.date.strftime('%Y-%m-%d %H:%M'),
            'currency': pay.currency,
            'comment': pay.comment,
            'debtor': pay.debtor.fio if pay.debtor else '',
            'money_circulation': pay.money_circulation.name if pay.money_circulation else '',
            'year': pay.date.strftime('%Y'),
            'month': pay.date.strftime('%m'),
            'day': pay.date.strftime('%d'),
        })

    return JsonResponse({'pay': pay_data})


def data_fin(request):
    context = {
        'clients':Debtor.objects.values('fio'),
        'deliver':Deliver.objects.values('name'),
        'employee':UserProfile.objects.values('first_name', 'last_name'),
    }
    return render(request, 'fin/data_fin.html', context)

from django.db.models import ExpressionWrapper

def first_day_we_stayed_deliver(debtor_id, year, month):
    target_date = date(year, month, 1)
    summa = 0

    models = [Shop, PayHistory, Bonus]

    for model in models:
        result = model.objects.filter(
            debtor_id=debtor_id,
            date=target_date
        ).aggregate(total=Sum('debt_new'))
        summa += result['total'] or 0

    return summa

def first_day_we_stayed_deliver(deliver_id, year, month):
    target_date = date(year, month, 1)
    summa = 0

    models = [Bonus, PayHistory, Recieve]

    for model in models:
        result = model.objects.filter(
            deliver_id=deliver_id,
            date=target_date
        ).aggregate(total=Sum('debt_new'))
        summa += result['total'] or 0

    return summa

def debet_kredit_fin(request):
    today = datetime.now()
    year = int(request.GET.get('year_filter', today.year))
    valyuta = request.GET.get('valyuta')
    debtor = Debtor.objects.all().values('id', 'fio')[:4]
    deliver = Deliver.objects.all().values('id', 'name')[:4]
    filters = {'year_filter': str(year), 'valyuta':valyuta}
    months_dict = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
        5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
        9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
    }

    shop = Shop.objects.filter(date__year=year)
    pay = PayHistory.objects.filter(date__year=year)
    recie = Recieve.objects.filter(date__year=year)

    if valyuta:
        shop = shop.filter(valyuta_id=valyuta)
        pay = pay.filter(valyuta_id=valyuta)
        recie = recie.filter(valyuta_id=valyuta)

    shops = shop.values('date__month', 'valyuta_id', 'debtor_id').annotate(
        total_price=Sum(
            ExpressionWrapper(
                F('cart__quantity') * F('cart__price'),
                output_field=IntegerField()
            )
        )
    )
    pay_history = pay.values('debtor_id', 'valyuta_id', 'date__month', 'deliver_id').annotate(
        summa=Sum('summa')
    )

    recieve = recie.values('date__month', 'deliver_id', 'valyuta_id').annotate(
        total=Sum('debt_old')
    )

    shops_dict = {(item['date__month'], item['debtor_id']): item for item in shops}
    pay_history_dict = {(item['date__month'], item['debtor_id']): item for item in pay_history}
        
    debtor_data = []

    for deb in debtor:
        debtor_dt = {
            'fio':deb['fio'],
            'month':[],
        }
        for month in range(1, 13):
            shop_data = shops_dict.get((month, deb['id']), {})
            pay_history_data = pay_history_dict.get((month, deb['id']), {})
            debtor_dt['month'].append({'month':month, 'total':shop_data.get('total_price', 0), 'summa':pay_history_data.get('summa', 0), 'debt':first_day_we_stayed_deliver(deb['id'], year, month)})
        debtor_data.append(debtor_dt)


    deliver_pay_history_dict = {(item['date__month'], item['deliver_id']): item for item in pay_history}
    deliver_recieve_dict = {(item['date__month'], item['deliver_id']): item for item in recieve}

    deliver_data = []

    for deli in deliver:
        deliver_dt = {
            'name':deli['name'],
            'month':[],
        }
        for month in range(1, 13):

            deliver_pay_history_data = deliver_pay_history_dict.get((month, deli['id']), {})
            deliver_recieve_data = deliver_recieve_dict.get((month, deli['id']), {})
            deliver_dt['month'].append({'month':month, 'summa':deliver_pay_history_data.get('summa', 0),
                                         'total':deliver_recieve_data.get('total', 0), 'debt':first_day_we_stayed_deliver(deli['id'], year, month)})

        deliver_data.append(deliver_dt)


    debtor_shops = shop.filter(debtor__isnull=False).values('date__month').annotate(
        total_price=Sum(
            ExpressionWrapper(
                F('cart__quantity') * F('cart__price'),
                output_field=IntegerField()
            )
        )
    )
    
    debtor_pay_history = pay.filter(debtor__isnull=False).values('date__month').annotate(
        summa=Sum('summa')
    )

    deliver_pay_history = pay.filter(deliver__isnull=False).values('date__month').annotate(
        summa=Sum('summa')
    )

    deliver_recieve = recie.filter(deliver__isnull=False ).values('date__month').annotate(
        total=Sum('debt_old')
    )

    itog_shops_dict = {(item['date__month']): item for item in debtor_shops}
    itog_pay_history_dict = {(item['date__month']): item for item in debtor_pay_history}

    itog_deliver_pay_dict = {(item['date__month']): item for item in deliver_pay_history}
    itog_deliver_recieve_dict = {(item['date__month']): item for item in deliver_recieve}

    itog = []
    deliver_itog = []

    for month in range(1, 13):
        dt = {
            'month':month,
            'total':itog_shops_dict.get(month, {}).get('total_price', 0),
            'summa':itog_pay_history_dict.get(month, {}).get('summa', 0),
        }
        et = {
            'month':month,
            'total':itog_deliver_recieve_dict.get(month, {}).get('total', 0),
            'summa':itog_deliver_pay_dict.get(month, {}).get('summa', 0),
        }
        itog.append(dt)

        deliver_itog.append(et)


    context = {
        'filters': filters,
        'months': list(months_dict.values()),
        'debtor_data':debtor_data,
        'itog':itog,
        'deliver_data':deliver_data,
        'deliver_itog':deliver_itog,
        'valyuta':Valyuta.objects.all(),
    }

    return render(request, 'fin/data_kredit_fin.html', context)


def debet_kredit_fin_copy(request):
    today = datetime.now()
    type_valyuta = request.GET.get('type_valyuta')
    year = int(request.GET.get('year_filter', today.year))

    filters = {'year_filter': str(year), 'type_valyuta': type_valyuta}
    months_dict = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
        5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
        9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
    }

    # Hammasini bitta query orqali olish
    results = ProductFilialDaily.objects.filter(date__year=year).values('date__month').annotate(
        rest_sum=Sum('rest')
    )
    shops = Shop.objects.filter(date__year=year).values('date__month').annotate(
        naqd_dollar=Sum('naqd_dollar'),
        naqd_som=Sum('naqd_som'),
        plastik=Sum('plastik'),
        click=Sum('click')
    )
    pay_histories = PayHistory.objects.filter(date__year=year).values('date__month').annotate(
        dollar=Sum('dollar'),
        som=Sum('som'),
        plastik=Sum('plastik'),
        click=Sum('click')
    )
    deliver_payments = DeliverPaymentsAll.objects.filter(date__year=year).values('date__month').annotate(
        left_sum=Sum('left'),
        received_total=Sum('received_total'),
        gave_total=Sum('gave_total')
    )

    # Ma'lumotlarni tezkor ajratish
    results_dict = {item['date__month']: item for item in results}
    shops_dict = {item['date__month']: item for item in shops}
    pay_histories_dict = {item['date__month']: item for item in pay_histories}
    deliver_payments_dict = {item['date__month']: item for item in deliver_payments}

    itogi_data = []
    deliver_data = []

    for month, month_name in months_dict.items():
        first_day = datetime(year, month, 1)

        # Valyuta bo'yicha hisob-kitob
        shop_data = shops_dict.get(month, {})
        pay_data = pay_histories_dict.get(month, {})
        result_data = results_dict.get(month, {'rest_sum': 0})

        if type_valyuta == '1':
            itogi = {
                'first_day': result_data['rest_sum'],
                'sotuv': shop_data.get('naqd_dollar', 0.0),
                'tolov': pay_data.get('dollar', 0.0),
            }
        else:
            itogi = {
                'first_day': result_data['rest_sum'],
                'sotuv': shop_data.get('naqd_som', 0.0) + shop_data.get('plastik', 0.0) + shop_data.get('click', 0.0),
                'tolov': pay_data.get('som', 0.0) + pay_data.get('plastik', 0.0) + pay_data.get('click', 0.0),
            }

        itogi_data.append(itogi)

        # Yetkazib beruvchi ma'lumotlari
        deliver_data.append({
            'first_day': deliver_payments_dict.get(month, {}).get('left_sum', 0),
            'sotuv': deliver_payments_dict.get(month, {}).get('received_total', 0),
            'tolov': deliver_payments_dict.get(month, {}).get('gave_total', 0),
        })

    context = {
        'filters': filters,
        'months': list(months_dict.values()),
        'itogi_data': itogi_data,
        'deliver_data': deliver_data,
    }

    return render(request, 'fin/data_kredit_fin.html', context)

def cf_fin(request):
    start = time.time()
    today = datetime.now()
    year = int(request.GET.get('year_filter', today.year))
    type_valyuta = request.GET.get('type_valyuta', '0')
    
    filters = {
        'year_filter':str(year),
        'type_valyuta':type_valyuta,
    }
    months_dict = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
        5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
        9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
    }

    
    payhistory_data = PayHistory.objects.filter(date__year=year).values('date__month').annotate(
        som=Coalesce(Sum('som'), 0 , output_field=FloatField()),
        dollar=Coalesce(Sum('dollar'), 0 , output_field=FloatField()),
    )

    payhistory_data_pl = PayHistory.objects.filter(date__year=year, som__lt=0, dollar__lt=0).values('date__month').annotate(
        som=Coalesce(Sum('som'), 0 , output_field=FloatField()),
        dollar=Coalesce(Sum('dollar'), 0 , output_field=FloatField()),
    )
    
    payhistory_dict = {item['date__month']: item for item in payhistory_data}
    payhistory_data_pl_dict = {item['date__month']: item for item in payhistory_data_pl}


    data = []
    data_pl = []
    for num, month in months_dict.items():
        dt = {
            'sum':payhistory_dict.get(num, {}).get('dollar' if type_valyuta == '1' else 'som', 0)
        }
        dt_pl = {
            'sum':payhistory_data_pl_dict.get(num, {}).get('dollar' if type_valyuta == '1' else 'som', 0)
        }
        data.append(dt)
        data_pl.append(dt_pl)


    context = {
        'filters':filters,
        'data':data,
        'months':[val for x, val in months_dict.items()],
        'data_pl':data_pl
    }
    end = time.time()
    return render(request, 'fin/cf_fin.html', context)

def daily_cf_fin(request):
    today = datetime.today()
    month = request.GET.get('month', today.month)
    year = request.GET.get('year', today.year)
    kassa = int(request.GET.get('kassa', 0))

    kirim = Kirim.objects.filter(qachon__year=year, qachon__month=month)
    chiqim = Chiqim.objects.filter(qachon__year=year, qachon__month=month)
    pay_history = PayHistory.objects.filter(date__year=year, date__month=month)

    if kassa:
        kirim = kirim.filter(kassa__kassa__id=kassa)
        chiqim = chiqim.filter(kassa__kassa__id=kassa)
        pay_history = pay_history.filter(kassa__kassa__id=kassa)

    filters = {
        'month':int(month),
        'year':str(year),
        'kassa':kassa,
    }

    days_of_month = calendar.monthrange(int(year), int(month))[1]
    days = list(range(1, days_of_month + 1))

    valyuta_list = Valyuta.objects.all()
    pay_history_list = list(pay_history.values('valyuta_id', 'date__day', 'debt_old', 'debt_new'))
    
    pay_history_dict = {}
    for record in pay_history_list:
        day = record['date__day']
        valyuta_id = record['valyuta_id']
        if (valyuta_id, day) not in pay_history_dict:
            pay_history_dict[(valyuta_id, day)] = {
                'debt_old': record['debt_old'],
                'debt_new': record['debt_new']
            }
    data = []
    for valyuta in valyuta_list:
        valyuta_id = valyuta.id
        valyuta_data = {
            'valyuta_id': valyuta_id,
            'valyuta_name': valyuta.name,
            'days': []
        }
        for day in days:
            day_kirim = kirim.filter(valyuta=valyuta, qachon__day=day).aggregate(
                all=Coalesce(Sum('summa'), 0, output_field=IntegerField())
            )['all']
            
            day_chiqim = chiqim.filter(valyuta=valyuta, qachon__day=day).aggregate(
                all=Coalesce(Sum('summa'), 0, output_field=IntegerField())
            )['all']
            
            ph_record = pay_history_dict.get((valyuta_id, day), {'debt_old': 0, 'debt_new': 0})
            valyuta_data['days'].append({
                'boshlangich_qoldik': ph_record['debt_old'],
                'kirim': day_kirim,
                'chiqim': day_chiqim,
                'yakuniy_qoldik': ph_record['debt_new']
            })
        data.append(valyuta_data)

    kirim_totals = kirim.values('qachon__day').annotate(
    total=Coalesce(Sum('summa'), 0, output_field=IntegerField())
    )
    chiqim_totals = chiqim.values('qachon__day').annotate(
        total=Coalesce(Sum('summa'), 0, output_field=IntegerField())
    )
    kirim_dict = {item['qachon__day']: item['total'] for item in kirim_totals}
    chiqim_dict = {item['qachon__day']: item['total'] for item in chiqim_totals}

    data_kirim = [{'sum': kirim_dict.get(day, 0)} for day in days]
    data_chiqim = [{'sum': chiqim_dict.get(day, 0)} for day in days]

    context = {
        'days_of_month': days,
        'filters':filters,
        'kassa':KassaNew.objects.filter(is_active=True),
        'data':data,
        'data_kirim':data_kirim,
        'data_chiqim':data_chiqim,
    }
    return render(request, 'fin/daily_cf_fin.html', context)


def daily_cf_fin_copy(request):
    today = datetime.today()
    month = request.GET.get('month', today.month)
    year = request.GET.get('year', today.year)
    type_val = request.GET.get('type_val')
    filters = {
        'month':int(month),
        'year':str(year),
        'type_val':str(type_val),
    }
    days_of_month = calendar.monthrange(int(year), int(month))[1]
    days = list(range(1, days_of_month + 1))

    fields = {
        'som': 'qancha_som',
        'dollar': 'qancha_dol',
        'plastik': 'plastik',
        'hisob_raqam': 'qancha_hisob_raqamdan',
    }
    selected_field = fields.get(type_val, 'qancha_som')
    
    kirim_data = (
        Kirim.objects.filter(qachon__year=year, qachon__month=month)
        .values('qachon__day')
        .annotate(
                sum=Coalesce(Sum(selected_field), 0, output_field=FloatField()),
                som=Coalesce(Sum('qancha_som'), 0, output_field=FloatField()),
                dollar=Coalesce(Sum('qancha_dol'), 0, output_field=FloatField()),
                plastik=Coalesce(Sum('plastik'), 0, output_field=FloatField()),
                hisob_raqam=Coalesce(Sum('qancha_hisob_raqamdan'), 0, output_field=FloatField())
            ))

    chiqim_data = (
        Chiqim.objects.filter(qachon__year=year, qachon__month=month)
        .values('qachon__day')
        .annotate(
            sum=Coalesce(Sum(selected_field), 0, output_field=FloatField()),
            som=Coalesce(Sum('qancha_som'), 0, output_field=FloatField()),
            dollar=Coalesce(Sum('qancha_dol'), 0, output_field=FloatField()),
            plastik=Coalesce(Sum('plastik'), 0, output_field=FloatField()),
            hisob_raqam=Coalesce(Sum('qancha_hisob_raqamdan'), 0, output_field=FloatField())
        ))

    kassa_daily = (
        KassaDaily.objects.filter(date__year=year, date__month=month)
        .values('date__day')
        .annotate(
            som=Coalesce(Sum('som'), 0, output_field=FloatField()),
            dollar=Coalesce(Sum('dollar'), 0, output_field=FloatField()),
            plastik=Coalesce(Sum('plastik'), 0, output_field=FloatField()),
            hisob_raqam=Coalesce(Sum('hisob_raqam'), 0, output_field=FloatField())
        )
    )

    kirim_dict = {item['qachon__day']: item['sum'] for item in kirim_data}
    chiqim_dict = {item['qachon__day']: item['sum'] for item in chiqim_data}
    

    kassa_daily_dict = {
        item['date__day']: {
            'som': item['som'],
            'dollar': item['dollar'],
            'plastik': item['plastik'],
            'hisob_raqam': item['hisob_raqam']
        }
        for item in kassa_daily
    }
    kirim_qoldik_dict = {
        item['qachon__day']: {
            'som': item['som'],
            'dollar': item['dollar'],
            'plastik': item['plastik'],
            'hisob_raqam': item['hisob_raqam']
        }
        for item in kirim_data
    }

    chiqim_qoldik_dict = {
        item['qachon__day']: {
            'som': item['som'],
            'dollar': item['dollar'],
            'plastik': item['plastik'],
            'hisob_raqam': item['hisob_raqam']
        }
        for item in chiqim_data
    }

    data_kirim = [{'sum': kirim_dict.get(day, 0)} for day in days]
    data_chiqim = [{'sum': chiqim_dict.get(day, 0)} for day in days]

    data_kassa_daily=[
            {
                'som': kassa_daily_dict.get(day, {}).get('som', 0),
                'dollar': kassa_daily_dict.get(day, {}).get('dollar', 0),
                'plastik': kassa_daily_dict.get(day, {}).get('plastik', 0),
                'hisob_raqam': kassa_daily_dict.get(day, {}).get('hisob_raqam', 0),
            }for day in days]

    data_qoldik_kirim=[
        {
            'som': kirim_qoldik_dict.get(day, {}).get('som', 0),
            'dollar': kirim_qoldik_dict.get(day, {}).get('dollar', 0),
            'plastik': kirim_qoldik_dict.get(day, {}).get('plastik', 0),
            'hisob_raqam': kirim_qoldik_dict.get(day, {}).get('hisob_raqam', 0),
        }for day in days]

    data_qoldik_chiqim =[
        {
            'som': chiqim_qoldik_dict.get(day, {}).get('som', 0),
            'dollar': chiqim_qoldik_dict.get(day, {}).get('dollar', 0),
            'plastik': chiqim_qoldik_dict.get(day, {}).get('plastik', 0),
            'hisob_raqam': chiqim_qoldik_dict.get(day, {}).get('hisob_raqam', 0),
        }for day in days]

    qoldik_data = []

    for day in days:
        qoldik = Kirim.objects.filter(qachon__year=year, qachon__month=month, qachon__day=day).last()
        qoldik_data.append({
            'som': getattr(qoldik, 'kassa_som_yangi', 0),
            'dollar': getattr(qoldik, 'kassa_dol_yangi', 0),
            'plastik': getattr(qoldik, 'kassa_plastik_yangi', 0),
            'hisob_raqam': getattr(qoldik, 'kassa_hisob_raqam_yangi', 0),
        })

    
    context = {
        'days_of_month': days,
        'data_kirim': data_kirim,
        'data_chiqim': data_chiqim,
        'data_kassa_daily': data_kassa_daily,
        'qoldik_data': qoldik_data,
        'data_qoldik_kirim': data_qoldik_kirim,
        'data_qoldik_chiqim': data_qoldik_chiqim,
        'filters':filters,
        'kassa':KassaNew.objects.filter(is_active=True),
    }
    return render(request, 'fin/daily_cf_fin.html', context)

from django.db.models import Value, Case, When

def xarid_fin(request):
    recieve = RecieveItem.objects.all().annotate(
        itog=Coalesce(
            Sum(
                Case(
                    When(som__gt=0, then=F('som') * F('quantity')),
                    default=F('dollar') * F('quantity'),
                    output_field=FloatField()
                )
            ), 
            Value(0),
            output_field=FloatField()
        )
    ).order_by('recieve__date')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    product = request.GET.getlist('product')
    deliver = request.GET.getlist('deliver')
    
    if start_date and end_date:
        recieve = recieve.filter(date__date__range=(start_date, end_date))

    if product:
        recieve = recieve.filter(product_id__in=product)

    if deliver:
        recieve = recieve.filter(recieve__deliver__id__in=deliver)
    
    paginator_recieve = Paginator(recieve, 50)
    page_number = request.GET.get('page')
    page_recieve = paginator_recieve.get_page(page_number)

    totals = {
        'quantity':recieve.aggregate(all=Coalesce(Sum('quantity'), 0, output_field=FloatField()))['all'],
        'itog':recieve.aggregate(all=Coalesce(Sum('itog'), 0, output_field=FloatField()))['all'],
    }
    
    context = {
        'recieve':page_recieve,
        'product':ProductFilial.objects.all().values('id', 'name'),
        'deliver':Deliver.objects.all().values('id', 'name'),
        'totals':totals,
    }
    return render(request, 'fin/xarid_fin.html', context)

def sotuv_fin(request):
    today = datetime.now()
    start_date = request.GET.get('start_date', today.replace(day=1).strftime('%Y-%m-%d') )
    end_date = request.GET.get('end_date', today.strftime('%Y-%m-%d'))
    cart = Cart.objects.filter(date__date__range=(start_date, end_date))

    filter = {
        'start_date':str(start_date),
        'end_date':str(end_date),
    }

    product = request.GET.getlist('product')
    debtor = request.GET.getlist('debtor')
    
    if product:
        cart = cart.filter(product_id__in=product)

    if debtor:
        cart = cart.filter(shop__debtor__id__in=debtor)

    paginator_cart = Paginator(cart, 50)
    page_number = request.GET.get('page')
    page_cart = paginator_cart.get_page(page_number)

    year = start_date[:4] if start_date else today.year 

    months_dict = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
        5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
        9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
    }
    carts = (
        Cart.objects.filter(date__year=year)
        .values('date__month')
        .annotate(
            quantity=Coalesce(Sum('quantity'), 0, output_field=FloatField()),
            total=Coalesce(Sum('total'), 0, output_field=FloatField())
        )
    )
    carts_dict = {item['date__month'] : { 'quantity':item['quantity'], 'total':item['total'] } for item in carts}

    carts_data = [
                {
                    'quantity':carts_dict.get(num, {}).get('quantity', 0),
                    'total':carts_dict.get(num, {}).get('total', 0),
                }
        for num , month in months_dict.items()
    ]
    totals = {
        'quantity':cart.aggregate(all=Coalesce(Sum('quantity'), 0, output_field=FloatField()))['all'],
        'total':cart.aggregate(all=Coalesce(Sum('total'), 0, output_field=FloatField()))['all'],
    }
    context = {
        'totals':totals,
        'cart':page_cart,
        'months': list(months_dict.values()),
        'carts_data':carts_data,
        'product':ProductFilial.objects.all().values('id', 'name'),
        'debtor':Debtor.objects.all().values('id', 'fio'),
        'filter':filter,
    }
    return render(request, 'fin/sotuv_fin.html', context)

def pl_fin(request):
    year_filter = request.GET.get('year', datetime.now().year)
    last_valyuta = Valyuta.objects.last()
    valyuta_filter = request.GET.get('valyuta', last_valyuta.id if last_valyuta else None)

    year = str(year_filter)

    categories = ProductCategory.objects.all()
    valyutas = Valyuta.objects.all()

    allcart = Cart.objects.filter(shop__valyuta_id=valyuta_filter)

    months = list(range(1, 13))

    total_marja = allcart.filter(shop__date__year=year).aggregate(sum=Sum(F('price') - F('bring_price')))['sum'] or 0
    marja_totals = [allcart.filter(shop__date__year=year, shop__date__month=m).aggregate(sum=Sum(F('price') - F('bring_price')))['sum'] or 0 for m in months]
    for i in categories:
        products = ProductFilial.objects.filter(category=i)
        i.months = []
        for m in months:
            carts = allcart.filter(shop__date__year=year, shop__date__month=m, product__category=i)
            total = carts.aggregate(sum=Sum(F('price') - F('bring_price')))['sum'] or 0
            i.months.append(total)
        i.percent = sum(i.months) / (total_marja if total_marja else 1) * 100

    
    total_cost = allcart.filter(shop__date__year=year).aggregate(sum=Sum(F('bring_price')))['sum'] or 0
    cost_totals = [allcart.filter(shop__date__year=year, shop__date__month=m).aggregate(sum=Sum(F('bring_price')))['sum'] or 0 for m in months]

    for i in categories:
        products = ProductFilial.objects.filter(category=i)
        i.cost_months = []
        for m in months:
            carts = allcart.filter(shop__date__year=year, shop__date__month=m, product__category=i)
            total = carts.aggregate(sum=Sum(F('bring_price')))['sum'] or 0
            i.cost_months.append(total)
        i.cost_percent = sum(i.cost_months) / (total_cost if total_cost else 1) * 100


    context = {
        'categories': categories,
        'total_marja': total_marja,
        'total_cost': total_cost,
        'valyutas': valyutas,
        'year': year,
        'valyuta_filter': int(valyuta_filter),
        'marja_totals': marja_totals,
        'cost_totals': cost_totals,

    }
    return render(request, 'fin/pl_fin.html', context)

def balans_fin(request):
    today = datetime.now()
    year = request.GET.get('year', today.year)
    valyuta = request.GET.get('valyuta')
    fields = {
        'som': 'som',
        'dollar': 'dollar',
    }
    selected_field = fields.get(valyuta, 'som')
    months_dict = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
        5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
        9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
    }
    main_tool = (
        MainTool.objects.filter(is_active=True, date__year=year)
        .values('date__month')
        .annotate(sum=Sum('summa'))
    )
    

    main_tool_dict = { item['date__month'] : { 'sum':item['sum']} for item in main_tool }

    main_tool_data = [
        {'sum':main_tool_dict.get(num, {}).get('sum', 0)}

        for num , month in months_dict.items()
    ]

    bebt_deliver = (
        DebtDeliver.objects.filter(date__year=year)
        .values('date__month')
        .annotate(sum=Coalesce(Sum(selected_field), 0, output_field=FloatField()))
    )
    bebt_deliver_dict = {item['date__month'] : { 'sum':item['sum']} for item in bebt_deliver}

    bebt_deliver_data = [
            {
                'sum':bebt_deliver_dict.get(num, {}).get('sum', 0),
            }
        for num , month in months_dict.items()
    ]

    kassa_daily = KassaDaily.objects.filter(date__year=year)
    
    kassa_daily_data = []

    reja_chiqim = (
        RejaChiqim.objects.filter(date__year=year, is_active=True)
        .values('date__month', 'valyuta_id')
        .annotate(sum=Sum('plan_total'))
    )

    reja_chiqim_dict = {
        (item['date__month'], item['valyuta_id']): {'sum': item['sum']} 
        for item in reja_chiqim
    }

    reja_chiqim_data = []

    for i in Valyuta.objects.all():
        dt_chiqim = {
            'valyuta_name': i.name,
            'month': []
        }
        for num, month in months_dict.items():
            chiqim_mon_dt = {
                'month': num,
                'summa': reja_chiqim_dict.get((num, i.id), {}).get('sum', 0)
            }
            dt_chiqim['month'].append(chiqim_mon_dt)
        reja_chiqim_data.append(dt_chiqim)

    
    for i in Valyuta.objects.all():
        dt = {
            'valyuta_name':i.name,
            'month':[]
        }
        for num , month in months_dict.items():
            mon_dt = {
                'month':num,
                'summa':kassa_daily.filter(date__month=num, valyuta=i).aggregate(all=Coalesce(Sum(selected_field), 0, output_field=IntegerField()))['all']
            }
            dt['month'].append(mon_dt)
        kassa_daily_data.append(dt)
    product = (
        ProductFilialDaily.objects.filter(date__year=year)
        .values('date__month')
        .annotate(sum=Coalesce(Sum(F('rest')-F('obyekt__quantity')), 0 , output_field=FloatField()))
    )

    product_dict = {
        product_loop['date__month'] : {'sum':product_loop['sum']}
        for product_loop in product
    }

    product_data = [
        {'sum':product_dict.get(num, {}).get('sum', 0)}

        for num , month in months_dict.items()
    ]

    context = {
        'months': list(months_dict.values()),
        'bebt_deliver_data':bebt_deliver_data,
        'kassa_daily_data':kassa_daily_data,
        'product_data':product_data,
        'main_tool_data':main_tool_data,
        'reja_chiqim_data':reja_chiqim_data,
    }
    return render(request, 'fin/balans_fin.html', context)

def majburiyat_fin(request):
    today = datetime.now().date()
    reja = RejaChiqim.objects.filter(is_active=True, is_majburiyat=True)
    reja_conf = RejaChiqim.objects.filter(is_active=True, is_majburiyat=True, is_confirmed=True)
    context = {
        'today':today,
        'reja':reja,
        'reja_conf':reja_conf,
        'kassa':KassaNew.objects.all(),
        'money_circulation':MoneyCirculation.objects.all(),
        'valyuta':Valyuta.objects.all(),
        'user_profile':UserProfile.objects.all(),
        'kurs':Course.objects.last().som or 0,
    }
    return render(request, 'fin/majburiyat_fin.html', context)

def get_week_blocks(year, month):
    result = []
    first_day = date(year, month, 1)
    start_day = first_day
    while start_day.weekday() != 0: 
        start_day += timedelta(days=1)
    while start_day.month == month:
        end_day = start_day + timedelta(days=6)
        if end_day.month == month:
            result.append((start_day, end_day))
        start_day += timedelta(days=7)
    return result


def get_monday_saturday_pairs(year, month):
    result = []
    current = date(year, month, 1)
    while current.weekday() != 0:  
        current += timedelta(days=1)
    count = 1
    while current.month == month:
        dushanba = current
        shanba = current + timedelta(days=5)
        if shanba.month != month:
            break  
        result.append({'dushanba': dushanba, 'shanba': shanba, 'count': count})
        # result.append((f'dushanba{count}', dushanba, f'shanba{count}', shanba))
        count += 1
        current += timedelta(days=7)
    return result




def tolov_kalendar_fin(request):
    today = datetime.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    weeks = get_monday_saturday_pairs(year, month)
    data_reja = []
    data_chiqim = []
    for week in weeks:
        dushanba = week['dushanba']
        shanba = week['shanba']
        
        weekly_reja_tushum = RejaTushum.objects.filter(is_active=True,payment_date__gte=dushanba, payment_date__lte=shanba)
        weekly_reja_chiqim = RejaChiqim.objects.filter(is_active=True ,payment_date__gte=dushanba, payment_date__lte=shanba)

        plan_reja = weekly_reja_tushum.aggregate(all=Coalesce(Sum('plan_total'), 0, output_field=IntegerField()))['all']
        total_reja = weekly_reja_tushum.aggregate(all=Coalesce(Sum('plan_total'), 0, output_field=IntegerField()))['all']

        if plan_reja or total_reja > 0:
            dt_reja = {
                'plan': plan_reja,
                'total': total_reja,
                'count':week['count']
            }
            data_reja.append(dt_reja)
        chiqim_plan = weekly_reja_chiqim.aggregate(all=Coalesce(Sum('plan_total'), 0, output_field=IntegerField()))['all']
        chiqim_total = weekly_reja_chiqim.aggregate(all=Coalesce(Sum('total'), 0, output_field=IntegerField()))['all']
        if chiqim_plan or chiqim_total > 0:
            dt_chiqim = {
                'plan': chiqim_plan,
                'total': chiqim_total,
                'count':week['count']
            }
            data_chiqim.append(dt_chiqim)
            
    filter = {
        "year":year,
        "month":str(month),
    }
    context = {
        'weeks':weeks,
        'data_reja':data_reja,
        'data_chiqim':data_chiqim,
        'filter':filter,
    }
    return render(request, 'fin/tolov_kalendar_fin.html', context)



def reja_tushum_fin(request):
    reja = RejaTushum.objects.all()
    today = datetime.today()
    year = request.GET.get('year', str(today.year))
    month = request.GET.get('month', str(today.month))
    filter = {
        "year":year,
        "month":month,
    }
    if year and month:
        reja = reja.filter(payment_date__year=year, payment_date__month=month)
    context = {
        'today':today,
        'reja':reja,
        'filter':filter,
        'debtor':Debtor.objects.all(),
        'deliver':Deliver.objects.all(),
        'external_income_user':ExternalIncomeUser.objects.filter(is_active=True),
        'valyuta':Valyuta.objects.all(),
        'money_circulation':MoneyCirculation.objects.all(),
        'kassa':KassaNew.objects.all(),
        'kurs':Course.objects.last().som or 0,
    }
    return render(request, 'fin/reja_tushum_fin.html', context)

def reja_tushum_fin_add(request):
    payment_date = request.POST.get('payment_date')
    plan_total = request.POST.get('plan_total')
    debtor = request.POST.get('debtor')
    comment = request.POST.get('comment')
    shop = request.POST.get('shop')
    valyuta = request.POST.get('valyuta')
    kurs = request.POST.get('kurs')
    where = request.POST.get('where')
    kassa = request.POST.get('kassa')
    money_circulation = request.POST.get('money_circulation')
    deliver = request.POST.get('deliver')
    external_income_user = request.POST.get('external_income_user')
    RejaTushum.objects.create(
        payment_date=payment_date,
        plan_total=plan_total,
        debtor_id=debtor,
        comment=comment,
        kurs=kurs,
        valyuta_id=valyuta,
        shop_id=shop,
        where=where,
        kassa_id=kassa,
        money_circulation_id=money_circulation,
        deliver_id=deliver,
        external_income_user_id=external_income_user,
    )
    return redirect(request.META['HTTP_REFERER'])

def reja_tushum_fin_edit(request, id):
    reja = RejaTushum.objects.get(id=id)
    payment_date = request.POST.get('payment_date')
    plan_total = request.POST.get('plan_total')
    debtor = request.POST.get('debtor')
    comment = request.POST.get('comment')
    valyuta = request.POST.get('valyuta')
    kurs = request.POST.get('kurs')
    where = request.POST.get('where')
    kassa = request.POST.get('kassa')
    money_circulation = request.POST.get('money_circulation')
    deliver = request.POST.get('deliver')
    external_income_user = request.POST.get('external_income_user')

    reja.payment_date=payment_date
    reja.kurs=kurs
    reja.where=where
    reja.plan_total=plan_total
    reja.debtor_id=debtor
    reja.comment=comment
    reja.valyuta_id=valyuta
    reja.kassa_id=kassa
    reja.money_circulation_id=money_circulation
    reja.deliver_id=deliver
    reja.external_income_user_id=external_income_user
    reja.save()
    return redirect(request.META['HTTP_REFERER'])

def reja_tushum_fin_del(request, id):
    RejaTushum.objects.filter(id=id).update(is_active=False)
    return redirect(request.META['HTTP_REFERER'])

def reja_chiqim_fin(request):
    reja = RejaChiqim.objects.filter(is_active=True)
    today = datetime.today()
    year = request.GET.get('year', str(today.year))
    month = request.GET.get('month', str(today.month))
    filter = {
        "year":year,
        "month":month,
    }
    if year and month:
        reja = reja.filter(date__year=year, date__month=month)
    context = {
        'today':today,
        'reja':reja,
        'filter':filter,
        'kassa':KassaNew.objects.all(),
        'money_circulation':MoneyCirculation.objects.all(),
        'valyuta':Valyuta.objects.all(),
        'user_profile':UserProfile.objects.all(),
        'kurs':Course.objects.last().som or 0,
    }
    return render(request, 'fin/reja_chiqim_fin.html', context)

def reja_chiqim_fin_add(request):
    payment_date = request.POST.get('payment_date')
    where = request.POST.get('where')
    plan_total = request.POST.get('plan_total')
    money_circulation = request.POST.get('money_circulation')
    comment = request.POST.get('comment')
    kassa = request.POST.get('kassa')
    user_profile = request.POST.get('user_profile')
    valyuta = request.POST.get('valyuta')
    kurs = request.POST.get('kurs')
    qaysi_oy = int(request.POST.get('qaysi_oy'))
    qaysi_yil = int(request.POST.get('qaysi_yil'))
    qaysi = date(qaysi_yil, qaysi_oy, 1)
    RejaChiqim.objects.create(
        payment_date=payment_date,
        where=where,
        plan_total=plan_total,
        money_circulation_id=money_circulation,
        comment=comment,
        kurs=kurs,
        user_profile_id=user_profile,
        valyuta_id=valyuta,
        kassa_id=kassa,
        qaysi=qaysi,
    )
    return redirect(request.META['HTTP_REFERER'])

def reja_chiqim_fin_edit(request, id):
    reja = RejaChiqim.objects.get(id=id)
    payment_date = request.POST.get('payment_date')
    where = request.POST.get('where')
    plan_total = request.POST.get('plan_total')
    money_circulation = request.POST.get('money_circulation')
    comment = request.POST.get('comment')
    kassa = request.POST.get('kassa')
    user_profile = request.POST.get('user_profile')
    valyuta = request.POST.get('valyuta')
    kurs = request.POST.get('kurs')
    qaysi_oy = int(request.POST.get('qaysi_oy'))
    qaysi_yil = int(request.POST.get('qaysi_yil'))
    qaysi = date(qaysi_yil, qaysi_oy, 1)
    
    reja.payment_date=payment_date
    reja.where=where
    reja.plan_total=plan_total
    reja.money_circulation_id=money_circulation
    reja.comment=comment
    reja.kassa_id=kassa
    reja.kurs=kurs
    reja.qaysi=qaysi
    reja.valyuta_id=valyuta
    reja.user_profile_id=user_profile
    reja.save()
    return redirect(request.META['HTTP_REFERER'])

def reja_chiqim_fin_del(request, id):
    RejaChiqim.objects.filter(id=id).update(is_active=False)
    return redirect(request.META['HTTP_REFERER'])


def asosiy_vosita_fin(request):
    today = datetime.now()
    year = int(request.GET.get('year', today.year))
    main_tool = MainTool.objects.filter(is_active=True)
    data = []
    for i in main_tool:
        dt = {
            'id':i.id,
            'name':i.name,
            'inventory_number':i.inventory_number,
            'quantity':i.quantity,
            'tool_type':i.tool_type,
            'summa':i.summa,
            'sum_wear_month_summa':i.sum_wear_month_summa,
            'sum_today_stayed':i.sum_today_stayed,
            'use_month':i.use_month,
            'wear_month_summa':i.wear_month_summa,
            'month':[]
        }
        data.append(dt)
        for month in range(1, 13):
            if year == i.date.year:
                query_month = i.date.month
                count_month = 0
                month_dt = {
                    'month':month,
                    'sum':0,
                }
                if query_month < month:
                    count_month+=1
                    if i.use_month >=count_month:
                        month_dt['sum'] = i.wear_month_summa * count_month

                dt['month'].append(month_dt)
            elif year > i.date.year:
                query_month = i.use_month - (12 - i.date.month) 
                count_month = 0
                month_dt = {
                    'month':month,
                    'sum':0,
                }
                if query_month >= month:
                    count_month+=1
                    if i.use_month >=count_month:
                        month_dt['sum'] = i.wear_month_summa * count_month

                dt['month'].append(month_dt)
    context = {
        'main_tool_type':MainToolType.objects.filter(is_active=True),
        'main_tool':data,
        'months': [i for i in range(1, 13)],
        'year':year
    }
    return render(request, 'fin/asosiy_vosita_fin.html', context)

@csrf_exempt
def add_main_tool_type(request):
    data = json.loads(request.body)
    name = data.get('name', '').strip()
    if not name:
        return JsonResponse({"error": "O'lchov birligi nomini kiriting!"}, status=400)
    created = MainToolType.objects.create(name=name)
    return JsonResponse({'data': {'id': created.id, 'name': created.name}}, status=201)

def add_main_tool(request):
    name = request.POST.get('name')
    number = request.POST.get('number')
    quantity = request.POST.get('quantity')
    tool_type = request.POST.get('tool_type')
    summa = request.POST.get('summa')
    use_month = request.POST.get('use_month')
    created = MainTool.objects.create(
        name=name,
        inventory_number=number,
        quantity=quantity,
        tool_type_id=tool_type,
        summa=summa,
        use_month=use_month,
    )
    created.wear_month_summa = int(summa)/int(use_month)
    created.save()
    return redirect(request.META['HTTP_REFERER'])

def edit_main_tool(request, id):
    name = request.POST.get('name')
    number = request.POST.get('number')
    quantity = request.POST.get('quantity')
    tool_type = request.POST.get('tool_type')
    summa = request.POST.get('summa')
    use_month = request.POST.get('use_month')
    created = MainTool.objects.get(id=id)
    created.name=name
    created.inventory_number=number
    created.quantity=quantity
    created.tool_type_id=tool_type
    created.summa=summa
    created.use_month=use_month
    created.wear_month_summa = int(summa)/int(use_month)
    created.save()
    return redirect(request.META['HTTP_REFERER'])

    
@csrf_exempt
def ajax_list_main_tool_type(request):
    main_tool_types = MainToolType.objects.filter(is_active=True).values("id", "name") 
    return JsonResponse({"data": list(main_tool_types)})



def ombor_fin(request):
    today = datetime.now()
    type_valyuta = request.GET.get('type_valyuta')
    year = int(request.GET.get('year_filter', today.year))
    type_valyuta = request.GET.get('type_valyuta', '0')

    filters = {
        'year_filter': str(year),
        'type_valyuta': type_valyuta,
    }

    months_dict = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
        5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
        9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
    }

    product_data = ProductFilialDaily.objects.filter(date__year=year).values('date__month').annotate(
        ostatka_dollar=Coalesce(Sum(F('rest') * F('obyekt__sotish_dollar')), 0, output_field=FloatField()),
        ostatka_som=Coalesce(Sum(F('rest') * F('obyekt__sotish_som')), 0, output_field=FloatField())
    )

    shop_data = Shop.objects.filter(date__year=year).values('date__month').annotate(
        pr_dollar=Coalesce(Sum(F('naqd_dollar')), 0, output_field=FloatField()),
        pr_som=Coalesce(Sum(F('naqd_som')), 0, output_field=FloatField())
    )

    product_dict = {item['date__month']: item for item in product_data}
    shop_dict = {item['date__month']: item for item in shop_data}

    data = []
    for num, month in months_dict.items():
        dt = {
            'ostatka': product_dict.get(num, {}).get('ostatka_dollar' if type_valyuta == '1' else 'ostatka_som', 0),
            'pr': shop_dict.get(num, {}).get('pr_dollar' if type_valyuta == '1' else 'pr_som', 0),
        }
        data.append(dt)

    context = {
        'filters': filters,
        'months': list(months_dict.values()),
        'data': data,
    }

    return render(request, 'fin/ombor_fin.html', context)


def b2b_shop_view(request):
    today = datetime.now()
    filial = Filial.objects.all()
    user_profile = UserProfile.objects.filter(user=request.user,staff=6)
    if user_profile:
        filial_ids = user_profile.values_list('filial__id', flat=True)
        filial = filial.filter(id__in=filial_ids)
       
    context = {
        'today':today,
        'filial':filial,
        'customer':Debtor.objects.all(),
        'contract':Contract.objects.filter(is_active=True),
        'product':ProductFilial.objects.filter(quantity__gt=0),
        'call_center' : UserProfile.objects.filter(staff=6),
        'valyuta' : Valyuta.objects.all(),
        'price_type':PriceType.objects.all(),
        'r_user':request.user
    }
    return render(request, 'b2b_shop_view.html', context)

@csrf_exempt
def b2b_shop_add(request):
    date = request.POST.get('date')
    customer = request.POST.get('customer')
    filial = request.POST.get('filial')
    contract = request.POST.get('contract')
    call_center = request.POST.get('call_center')
    comment = request.POST.get('text')
    is_savdo = request.POST.get('is_savdo')
    valyuta = request.POST.get('valyuta')
    type_price = request.POST.get('type_price')
    kurs = Course.objects.last()
    saler = UserProfile.objects.get(id=call_center)
    sh = Shop.objects.create(
        date=date,
        debtor_id=customer,
        filial_id=filial,
        contract_id=contract,
        saler=saler,
        call_center=saler.first_name,
        comment=comment,
        kurs=kurs.som if kurs else 0,
        b2c=False,
        is_savdo=is_savdo,
        valyuta_id=valyuta,
        type_price_id=type_price,
    )
    return JsonResponse({'success': True, 'order_id':sh.id})

from django.template.loader import render_to_string
from django.db import transaction

def payment_shop_ajax(request, id):
    data = json.loads(request.body)
    shop = Shop.objects.get(id=id)
    amount = 0
    nasiya = 0
    kurs = Course.objects.last()
    is_dollar = shop.valyuta.is_dollar

    for i in data:
        if 'kassa_id' in i and 'amount' in i:
            kassa = KassaMerge.objects.get(id=i['kassa_id'])
            amount += int(i['amount'])
            kassa.summa += int(i['amount'])
            kassa.save()
        if 'nasiya' in i:
            nasiya += int(i['nasiya'])
    if is_dollar:
        shop.naqd_dollar = round(amount / kurs.som, 2)
        shop.nasiya_dollar = round(nasiya / kurs.som, 2)
    else:
        shop.naqd_som = amount
        shop.nasiya_som = nasiya
    objec, create = PayHistory.objects.get_or_create(shop=shop, debtor=shop.debtor)
    objec.comment = 'B2B savdo'
    objec.valyuta = shop.valyuta
    objec.summa += amount
    objec.type_pay = 2
    objec.save()
    shop.save()
    shop.debtor.refresh_debt()
    return JsonResponse({'success': True})

def product_remove_quantity(request, shop_id):
    data = json.loads(request.body)
    shop = Shop.objects.get(id=shop_id)
    debtor = Debtor.objects.get(id=shop.debtor.id)
    total = 0

    with transaction.atomic():
        for i in data:
            pr = ProductFilial.objects.get(id=i['product_id'])
            if shop.is_savdo:
                pr.quantity -= i['quantity']
            else:
                pr.quantity += i['quantity']
            total += i['total']
            pr.save()

        total_nasiya = 0
        if shop.nasiya_dollar and shop.kurs:
            total_nasiya += shop.nasiya_dollar * shop.kurs
        if shop.naqd_som:
            total_nasiya += shop.naqd_som

        obj, created = RejaTushum.objects.get_or_create(shop=shop)
        obj.plan_total = shop.baskets_total_price or 0
        obj.total = total_nasiya
        obj.debtor = shop.debtor
        obj.valyuta = shop.valyuta
        obj.comment = shop.comment or ""
        obj.kurs = shop.kurs or 0
        obj.payment_date = shop.debt_return
        obj.from_shop = True
        obj.save()
    return JsonResponse({'success': True})
    

def b2b_shop_ajax(request, product_id):
    shop = Shop.objects.get(id=product_id)
    type_id = request.GET.get('type_id')
    carts = Cart.objects.filter(shop=shop)
    user_profile = UserProfile.objects.filter(user=request.user,staff=6).last()

    fields = ''
    if shop.valyuta and shop.valyuta.is_dollar:
        fields = 'price_types__price_dollar'
    else :
        fields = 'price_types__price'
    kurs = Course.objects.last()
    context = {
        'today':datetime.today(),
        'filial':Filial.objects.all(),
        'customer':Debtor.objects.all(),
        'contract':Contract.objects.filter(is_active=True),
        'product':ProductFilial.objects.filter(quantity__gt=0, price_types__type=shop.type_price).annotate(price_ty=Coalesce(Sum(fields, output_field=FloatField()), Value(0.0))),
        'user_profile':UserProfile.objects.all(),
        'groups':Groups.objects.all(),
        'call_center':UserProfile.objects.filter(staff=6),
        'price_type':PriceType.objects.all(),
        'valyuta' : Valyuta.objects.all(),
        'product_id':product_id,
        'kassa':KassaMerge.objects.filter(kassa__filial=shop.filial),
        'shop':shop,
        'kurs':kurs.som if kurs else 0,
        'carts':carts,
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  
        product_html = render_to_string('product_list.html',
         {'product': ProductFilial.objects.filter(price_types__type_id=type_id).annotate(price_ty=Coalesce(Sum('price_types__price', output_field=FloatField()), Value(0.0)))}, request)
        return JsonResponse({'product_html': product_html})
    return render(request, 'b2b_shop_ajax.html', context)

def b2b_shop_ajax_add(request, product_id):
    data = json.loads(request.body)
    sh = Shop.objects.get(id=product_id)
    for i in data :
        if i['quantity'] and i['total'] and i['product_id']:
            Cart.objects.create(
                shop_id=product_id,
                quantity=int(i['quantity']),
                total=int(i['total']),
                price=int(i['price']),
                product_id=int(i['product_id'])
            )
    sh.is_finished = True
    sh.save()
    sh.debtor.refresh_debt()
    return JsonResponse({'success': True})

def ajax_reja_tushum_list(request, shop_id):
    return JsonResponse({'reja_tushum': RejaTushum.objects.filter(shop_id=shop_id).count()})



def b2b_shop_ajax_add_one(request, product_id):
    data = json.loads(request.body)
    sh = Shop.objects.get(id=product_id)
    if data['quantity']:
        obj, created = Cart.objects.get_or_create(shop_id=product_id,product_id=int(data['product_id']))
        obj.quantity=data['quantity']
        obj.total=data['total']
        obj.price=data['price']
        obj.skidka_total=data['skidka']
        obj.save()
        sh.is_finished = True
        sh.save()
    sh.debtor.refresh_debt()
    return JsonResponse({'success': True})

def b2b_shop_ajax_cart_delete(request, product_id):
    data = json.loads(request.body)
    if int(data['product_id']):
        cart = Cart.objects.get(shop_id=product_id,product_id=int(data['product_id']))
        product = ProductFilial.objects.get(id=int(data['product_id']))
        product.quantity += cart.quantity
        product.save()
        cart.delete()
    return JsonResponse({'success': True})



@csrf_exempt
def b2b_shop_ajax_edit(request, id):
    comment = request.POST.get('text')
    nds_count = request.POST.get('nds_count')
    debt_return = request.POST.get('debt_return')
    
    sh = Shop.objects.get(id=id)
    if comment:
        sh.comment=comment
    if nds_count:
        sh.nds_count=nds_count
    if debt_return:
        sh.debt_return=debt_return
    sh.save()
    return JsonResponse({'success': True})

def price_type_filter_ajax(request):
    data = json.loads(request.body)
    price_type = PriceType.objects.get(id=data['type_id'])
    ids = [i['id'] for i in data.get('products', [])]
    product = ProductPriceType.objects.filter(type=price_type, product_id__in=ids)
    data = []
    for i in product:
        dt = {
            'id':i.product.id,
            'name':i.product.name,
            'quantity':i.product.quantity,
            'price':i.price,
        }
        data.append(dt)
    return JsonResponse({'success': True, 'data':data})

def nds_ajax(request):
    nds =  NDS.objects.last()
    return JsonResponse({'success': True, 'count':nds.perecent})

def add_product_list(request, id):
    sh = Shop.objects.get(id=id)

    name = request.POST.get('name')
    som = request.POST.get('som')
    quantity = request.POST.get('quantity')
    barcode = request.POST.get('barcode')
    groups = request.POST.get('groups')
    measurement = request.POST.get('measurement')
    valyuta = request.POST.get('valyuta')
    query_valyuta = Valyuta.objects.get(id=valyuta)

    pr = ProductFilial.objects.create(
        name=name,
        som=som if query_valyuta.is_dollar == False else 0,
        dollar=som if query_valyuta.is_dollar else 0,
        quantity=quantity,
        barcode=barcode,
        group_id=groups,
        measurement=measurement,
        filial=sh.filial,
        valyuta=query_valyuta
    )
    product = {
        'id':pr.id,
        'name':pr.name,
        'quantity':pr.quantity,
        'som':pr.dollar if query_valyuta.is_dollar else pr.som,
    }
    return JsonResponse({'success': True, 'product':product})


def nds_view(request):
    nds = NDS.objects.last()
    if request.method == 'POST':
        if nds:
            perecent = request.POST.get('perecent')
            nds.perecent = perecent
            nds.save()
        else :
            NDS.objects.create(
                perecent=perecent
            )
    context = {
        'nds':nds,
    }
    return render(request, 'nds_page.html', context)

def filial_list(request):
    context = {
        'filial':Filial.objects.filter(is_activate=True),
        'valyuta':Valyuta.objects.all(),
    }
    return render(request, 'filial_list.html', context)

def filial_add(request):
    name = request.POST.get('name')
    address = request.POST.get('address')
    qarz_som = request.POST.get('qarz_som')
    qarz_dol = request.POST.get('qarz_dol')
    savdo_puli_som = request.POST.get('savdo_puli_som')
    savdo_puli_dol = request.POST.get('savdo_puli_dol')
    valyuta = request.POST.get('valyuta')

    Filial.objects.create(
        name=name,
        address=address,
        qarz_som=qarz_som,
        qarz_dol=qarz_dol,
        savdo_puli_som=savdo_puli_som,
        savdo_puli_dol=savdo_puli_dol,
        valyuta_id=valyuta,
    )
    return redirect(request.META['HTTP_REFERER'])


def filial_edit(request, id):
    name = request.POST.get('name')
    address = request.POST.get('address')
    qarz_som = request.POST.get('qarz_som')
    qarz_dol = request.POST.get('qarz_dol')
    savdo_puli_som = request.POST.get('savdo_puli_som')
    savdo_puli_dol = request.POST.get('savdo_puli_dol')
    valyuta = request.POST.get('valyuta')
    filial = Filial.objects.get(id=id)
    filial.name=name
    filial.address=address
    filial.qarz_som=qarz_som
    filial.qarz_dol=qarz_dol
    filial.savdo_puli_som=savdo_puli_som
    filial.savdo_puli_dol=savdo_puli_dol
    filial.valyuta_id=valyuta
    filial.save()
    return redirect(request.META['HTTP_REFERER'])

def filial_del(request, id):
    filial = Filial.objects.get(id=id)
    filial.is_activate = False
    filial.save()
    return redirect(request.META['HTTP_REFERER'])


def externalincomeuser(request):
    pass
    valutas = Valyuta.objects.all()
    partners = ExternalIncomeUser.objects.all()
    
    context = {
        'income': partners,
        'type_income':ExternalIncomeUserTypes.objects.all(),
        'valyuta':valutas,
        'cashes':KassaNew.objects.filter(is_active=True),
    }

    context['total_haq'] = [
            {'summa': Wallet.objects.filter(partner__in=partners, valyuta=val, summa__gt=0).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all']}
            for val in valutas
        ]
    context['total_qarz'] = [
            {'summa': Wallet.objects.filter(partner__in=partners, valyuta=val, summa__lt=0).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all']}
            for val in valutas
        ]
    return render(request, 'externalincomeuser.html', context)

def externalincomeuser_detail(request, id):
    income = ExternalIncomeUser.objects.get(id=id)
    valyuta = Valyuta.objects.all()
    debt_shot = Wallet.objects.filter(partner_id=id)
    today = datetime.now().date()

    start_date = request.GET.get('start_date', today.replace(day=1))
    end_date = request.GET.get('end_date', today)

    filters = {
        'start_date': str(start_date),
        'end_date': str(end_date),
    }
    pay = PayHistory.objects.filter(external_income_user_id=id, date__date__range=(start_date, end_date))
    bonus = Bonus.objects.filter(partner_id=id, date__date__range=(start_date, end_date))

    data = []
    for i in pay:
        dt = {
            'id': i.id,
            'date': i.date,
            'comment': i.comment,
            'valyuta': i.valyuta,
            'debt_new': i.debt_new,
        }
        if i._meta.model_name == 'payhistory':
            if i.type_pay == 1:
                dt['type_payment'] = 'Pul olindi'
                dt['pay_summa'] = i.summa
            else:
                dt['type_payment'] = 'Pul Berildi'
                dt['give_summa'] = i.summa
        
        elif i._meta.model_name == 'bonus':
            dt['type_payment'] = 'Bonus berildi'
            if i.summa <= 0:
                dt['pay_summa'] = i.summa
            else:
                dt['give_summa'] = i.summa

        data.append(dt)
    summa_total_for_valyuta = []
    for val in valyuta:
        pay_summa = pay.filter(valyuta=val, type_pay=1).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all']
        pay_ow_suma = pay.filter(valyuta=val, type_pay=2).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all']
        dt_sum_valyuta = {
            'valyuta':val.id,
            'pay_pay_summa':pay_summa ,
            'pay_give_summa':pay_ow_suma,
        }
        summa_total_for_valyuta.append(dt_sum_valyuta)

    data_start_sum = []
    for valu in valyuta:
        star_dt = {
            'valyuta':valu,
            'start': debt_shot.filter(valyuta=valu).last().start_summa if debt_shot.filter(valyuta=valu) else 0
        }
        data_start_sum.append(star_dt)
    context = {
        'income':income,
        'valyuta':valyuta,
        'debt_shot':debt_shot,
        'filters':filters,
        'data':data,
        'summa_total_for_valyuta':summa_total_for_valyuta,
        'data_start_sum':data_start_sum,
    }
    return render(request, 'externalincomeuser_detail.html', context)

def external_income_user_debt_create(request, id):
    income = ExternalIncomeUser.objects.get(id=id)
    valyuta = request.POST.get('valyuta')
    start_summa = request.POST.get('start_summa')
    obj, create = ExternalIncomeUserDebt.objects.get_or_create(income=income, valyuta_id = valyuta)
    obj.start_summa = start_summa
    obj.save()
    income.income_refresh_debt()
    return redirect(request.META['HTTP_REFERER'])


def externalincomeuser_add(request):
    full_name = request.POST.get('full_name')
    phone = request.POST.get('phone')
    type = request.POST.get('type')
    tartib_raqam = request.POST.get('tartib_raqam')
    ExternalIncomeUser.objects.create(
        full_name=full_name,
        phone=phone,
        type_id=type,
        tartib_raqam=tartib_raqam,
    )
    return redirect(request.META['HTTP_REFERER'])


def external_income_user_types_add(request):
    name = request.POST.get('name')
    ExternalIncomeUserTypes.objects.create(
        name=name,
    )
    return redirect(request.META['HTTP_REFERER'])


def externalincomeuser_edit(request, id):
    full_name = request.POST.get('full_name')
    phone = request.POST.get('phone')
    type = request.POST.get('type')
    tartib_raqam = request.POST.get('tartib_raqam')
    query = ExternalIncomeUser.objects.get(id=id)
    query.full_name=full_name
    query.phone=phone
    query.type_id=type
    query.tartib_raqam=tartib_raqam
    query.save()
    return redirect(request.META['HTTP_REFERER'])

def income_payment(request, id):
    income = ExternalIncomeUser.objects.get(id=id)
    summa = int(request.POST.get('summa', 0))
    comment = request.POST.get('comment')
    valyuta = request.POST.get('valyuta')
    PayHistory.objects.create(
        external_income_user=income,
        summa=summa,
        comment=comment,
        valyuta_id=valyuta,
        type_pay=1,
    )
    ExternalIncomeUserPayment.objects.create(
        external_income_user=income,
        valyuta_id=valyuta,
        summa=summa,
        type_pay=1,
        comment=comment,
    )
    income.income_refresh_debt()
    return redirect(request.META['HTTP_REFERER'])


def income_give(request, id):
    income = ExternalIncomeUser.objects.get(id=id)
    summa = int(request.POST.get('summa', 0))
    comment = request.POST.get('comment')
    valyuta = request.POST.get('valyuta')
    PayHistory.objects.create(
        external_income_user=income,
        valyuta_id=valyuta,
        summa=summa,
        comment=comment,
        type_pay=2,
    )
    ExternalIncomeUserPayment.objects.create(
        external_income_user=income,
        valyuta_id=valyuta,
        summa=summa,
        type_pay=2,
        comment=comment,
    )
    income.income_refresh_debt()
    return redirect(request.META['HTTP_REFERER'])


def valyuta_list(request):
    valyuta = Valyuta.objects.all()
    context = {
        'valyuta':valyuta
    }
    return render(request, 'valyuta.html', context)

def valyuta_add(request):
    name = request.POST.get('name')
    Valyuta.objects.create(name=name)
    return redirect(request.META['HTTP_REFERER'])

def valyuta_edit(request,id):
    name = request.POST.get('name')
    valyuta = Valyuta.objects.get(id=id)
    valyuta.name=name
    valyuta.save()
    return redirect(request.META['HTTP_REFERER'])


def kassa_merge(request):
    merge = KassaMerge.objects.filter(is_active=True)
    context = {
        'merge':merge,
        'valyuta':Valyuta.objects.all(),
        'kassa':KassaNew.objects.filter(is_active=True),
    }
    return render(request, 'kassa_merge.html', context)

def kassa_merge_add(request):
    kassa = request.POST.get('kassa')
    valyuta = request.POST.get('valyuta')
    start_summa = int(request.POST.get('start_summa') or 0)
    summa = int(request.POST.get('summa') or 0)
    start_date = request.POST.get('start_date')
    obj , created =  KassaMerge.objects.get_or_create(kassa_id=kassa,valyuta_id=valyuta)
    obj.start_summa+=start_summa
    obj.summa+=summa
    obj.start_date=start_date
    obj.save()
    return redirect(request.META['HTTP_REFERER'])

def kassa_merge_edit(request, id):
    # kassa = request.POST.get('kassa')
    # valyuta = request.POST.get('valyuta')
    start_summa = request.POST.get('start_summa')
    summa = request.POST.get('summa')
    start_date = request.POST.get('start_date')
    merge = KassaMerge.objects.get(id=id)
    # merge.kassa_id=kassa
    # merge.valyuta_id=valyuta
    merge.start_summa=start_summa
    merge.summa=summa
    merge.start_date=start_date
    merge.save()
    return redirect(request.META['HTTP_REFERER'])


def kassa_merge_del(request, id):
    merge = KassaMerge.objects.filter(id=id).update(is_active=False)
    return redirect(request.META['HTTP_REFERER'])


def kassa_new_list(request):
    context = {
        'kassa':KassaNew.objects.filter(is_active=True),
        'filial':Filial.objects.filter(is_activate=True),
        'use':User.objects.all(),
    }
    return render(request, 'kassa_new_list.html', context)

def kassa_new_add(request):
    name = request.POST.get('name')
    filial = request.POST.get('filial')
    kassa_user = request.POST.get('kassa_user')
    is_main = True if request.POST.get('is_main') == 'on' else False
    KassaNew.objects.create(name=name, filial_id=filial, is_main=is_main, kassa_user_id=kassa_user)
    return redirect(request.META['HTTP_REFERER'])

def kassa_new_edit(request,id):
    name = request.POST.get('name')
    filial = request.POST.get('filial')
    kassa_user = request.POST.get('kassa_user')
    kas = KassaNew.objects.get(id=id)
    is_main = True if request.POST.get('is_main') == 'on' else False
    kas.name=name
    kas.is_main=is_main
    kas.kassa_user_id=kassa_user
    if is_main:
        kas.filial_id=''
    else:
        kas.filial_id=filial
    kas.save()
    return redirect(request.META['HTTP_REFERER'])



def filial_kassalar(request):
    kassa = KassaMerge.objects.filter(is_active=True, kassa__is_main=False)
    filial = Filial.objects.all()
    data = []
    for i in filial:
        dt = {
            'name':i.name,
            'valyuta':[
                {'name':val.name , 'summa': kassa.filter(kassa__filial=i, valyuta=val).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all'] }
                for val in Valyuta.objects.all()
            ],
        }
        data.append(dt)
    context = {
        'kassa':kassa,
        'data':data
    }
    return render(request, 'filial_kassalar.html', context)


def customer_debt_create(request, id):
    customer = Debtor.objects.get(id=id)
    valyuta = request.POST.get('valyuta')
    start_summa = request.POST.get('start_summa')
    # obj, create = CustomerDebt.objects.get_or_create(customer=customer, valyuta_id = valyuta)
    # obj.start_summa = start_summa
    # obj.save()
    # customer.refresh_debt()
    return redirect(request.META['HTTP_REFERER'])


def set_start_summa(request):
    debtor = request.POST.get('debtor')
    partner = request.POST.get('partner')
    deliver = request.POST.get('deliver')

    date = request.POST.get('date')
    valuta = request.POST.get('valuta')
    summa = request.POST.get('summa')

    if debtor:
        wallet = Wallet.objects.filter(customer_id=debtor, valyuta_id=valuta).last() or Wallet.objects.create(customer_id=debtor, valyuta_id=valuta) 
    
    elif partner:
        wallet = Wallet.objects.filter(partner_id=partner, valyuta_id=valuta).last() or Wallet.objects.create(partner_id=partner, valyuta_id=valuta) 

    elif deliver:
        wallet = Wallet.objects.filter(deliver_id=deliver, valyuta_id=valuta).last() or Wallet.objects.create(deliver_id=deliver, valyuta_id=valuta) 
    
    else:
        messages.error(request, 'Amaliyot topilmadi')
        return redirect(request.META['HTTP_REFERER'])
    

    Wallet.objects.filter(id=wallet.id).update(start_summa=summa)
    # wallet.update(start_summa=summa)


    if debtor:
        Debtor.objects.get(id=debtor).refresh_debt()

    if partner:
        ExternalIncomeUser.objects.get(id=partner).refresh_debt()

    if deliver:
        Deliver.objects.get(id=deliver).refresh_debt()
    
    messages.success(request, "Muvaffaqiyatli saqlandi")

    return redirect(request.META['HTTP_REFERER'])
    

def add_bonus(request):
    debtor = request.POST.get('debtor')
    partner = request.POST.get('partner')
    deliver = request.POST.get('deliver')

    valuta = request.POST.get('valuta')
    summa = request.POST.get('summa')
    comment = request.POST.get('comment')
    date = request.POST.get('date')


    if debtor:
        wallet = Bonus.objects.create(debtor_id=debtor, valyuta_id=valuta, summa=summa, date=date, comment=comment)
        Debtor.objects.get(id=debtor).refresh_debt()
    
    elif partner:
        wallet = Bonus.objects.create(partner_id=partner, valyuta_id=valuta, summa=summa, date=date, comment=comment)
        ExternalIncomeUser.objects.get(id=partner).refresh_debt()

    elif deliver:
        wallet = Bonus.objects.create(deliver_id=deliver, valyuta_id=valuta, summa=summa, date=date, comment=comment)
        Deliver.objects.get(id=deliver).refresh_debt()
    
    else:
        messages.error(request, 'Amaliyot topilmadi')
        return redirect(request.META['HTTP_REFERER'])
    

    messages.success(request, "Muvaffaqiyatli saqlandi")

    return redirect(request.META['HTTP_REFERER'])
    


def majburiyat_chiqim_fin_add(request):
    deadline = request.POST.get('deadline')
    date = request.POST.get('date')
    where = request.POST.get('where')
    plan_total = request.POST.get('plan_total')
    money_circulation = request.POST.get('money_circulation')
    comment = request.POST.get('comment')
    kassa = request.POST.get('kassa')
    user_profile = request.POST.get('user_profile')
    valyuta = request.POST.get('valyuta')
    kurs = request.POST.get('kurs')
    
    RejaChiqim.objects.create(
        deadline=deadline,
        date=date,
        where=where,
        plan_total=plan_total,
        money_circulation_id=money_circulation,
        comment=comment,
        kurs=kurs,
        user_profile_id=user_profile,
        valyuta_id=valyuta,
        kassa_id=kassa,
        is_majburiyat=True,
    )
    return redirect(request.META['HTTP_REFERER'])


def reja_chiqim_bajarish(request, id):
    reja = RejaChiqim.objects.get(id=id)
    plan_total_raw = request.POST.get('plan_total', '0')
    plan_total_clean = plan_total_raw.replace('\xa0', '').replace(' ', '')  
    plan_total = int(plan_total_clean)

    kurs = request.POST.get('kurs')
    kassa_id = request.POST.get('kassa')
    valyuta = request.POST.get('valyuta')
    comment = request.POST.get('comment')
    kassa = get_object_or_404(KassaMerge, kassa_id=kassa_id, valyuta_id=valyuta)
    kassa.summa -= plan_total
    kassa.save()
    pay = PayHistory.objects.create(
        kassa=kassa,
        valyuta_id=valyuta,
        summa=plan_total,
        comment=comment,
        type_pay=2
    )
    Chiqim.objects.create(
        payhistory=pay,
        izox=comment,
        summa=plan_total,
        valyuta_id=valyuta,
        kassa=kassa,
        reja_chiqim=reja,
    )
    reja.is_confirmed = True
    reja.save()
    return redirect(request.META['HTTP_REFERER'])



def todays_practices(request):
    today = datetime.today().date()
    shop = Shop.objects.filter(date__date=today)
    pay = PayHistory.objects.filter(date__date=today)
    query_valyuta = Valyuta.objects.all()
    user_profile = UserProfile.objects.filter(user=request.user).last()
    
    if user_profile.filial:
        shop = shop.filter(filial=user_profile.filial)
        pay = pay.filter(filial=user_profile.filial)

    # filial = request.GET.get('filial')
    # valyuta = request.GET.get('valyuta')
    # if filial:
    #     shop = shop.filter(filial_id=filial)
    #     pay = pay.filter(filial_id=filial)
    # if valyuta:
    #     shop = shop.filter(valyuta_id=valyuta)
    #     pay = pay.filter(valyuta_id=valyuta)
    
    totals_shop = []
    for i in query_valyuta:
        sh_dt = {
            'name': i.name,
            'summa': shop.filter(
                date__date=today,
                valyuta=i
            ).aggregate(
                total_price=Sum(
                    ExpressionWrapper(
                        F('cart__quantity') * F('cart__price'),
                        output_field=IntegerField()
                    )
                )
            )['total_price'],
            'pay':pay.filter(date__date=today, valyuta=i).aggregate(all=Coalesce(Sum('summa'), 0, output_field=IntegerField()))['all'],
        }
        totals_shop.append(sh_dt)

        
    context = {
        'shop':shop,
        'pay':pay,
        'filial':Filial.objects.filter(is_activate=True),
        'valyuta':query_valyuta,
        'totals_shop':totals_shop,
    }
    return render(request, 'todays_practices.html', context)



def reviziya(request):
    today = datetime.now().date()
    start_date = request.GET.get('start_date', today.replace(day=1))
    end_date = request.GET.get('end_date', today)
    filial = request.GET.get('filial')
    filters = {
        'start_date':str(start_date),
        'end_date':str(end_date),
        'filial':filial,
    }
    revision = Revision.objects.filter(is_completed=False)

    revision = revision.filter(date__range=(start_date, end_date))
    if filial:
        revision = revision.filter(filial_id=filial)

    context = {
        'revision': revision,
        'today':today,
        'filters':filters,
        'filial': Filial.objects.filter(is_activate=True),
        'price_type': PriceType.objects.filter(is_activate=True),
        'valyuta':Valyuta.objects.all(),
        'user_profile':UserProfile.objects.all(),
    }
    return render(request, 'reviziya.html', context)


def revision_complate(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    filial = request.GET.get('filial')
    today = datetime.now().date()
    filters = {
        'start_date':start_date,
        'end_date':end_date,
        'filial':filial,
    }
    revision = Revision.objects.filter(is_completed=True)

    if start_date and end_date:
        revision = revision.filter(date__range=(start_date, end_date))
    if filial:
        revision = revision.filter(filial_id=filial)

    context = {
        'revision': revision,
        'today':today,
        'filters':filters,
    }
    return render(request, 'revision_complate.html', context)

def revision_complate_items(request ,id):
    revision = Revision.objects.get(id=id)
    item = RevisionItems.objects.filter(revision=revision)
    totals = {
        'quantity':item.aggregate(all=Coalesce(Sum('quantity'), 0, output_field=FloatField()))['all'],
        'old_quantity':item.aggregate(all=Coalesce(Sum('old_quantity'), 0, output_field=FloatField()))['all'],
        'som_arrival_price':item.aggregate(all=Coalesce(Sum(F('som_arrival_price')*F('quantity')), 0, output_field=FloatField()))['all'],
        'dollar_arrival_price':item.aggregate(all=Coalesce(Sum(F('dollar_arrival_price')*F('quantity')), 0, output_field=FloatField()))['all'],
        'farqi':item.aggregate(all=Coalesce(Sum(F('quantity')-F('old_quantity')), 0, output_field=FloatField()))['all'],
        'farqi_som_arrival_price':item.aggregate(all=Coalesce(Sum((F('quantity')-F('old_quantity'))*F('som_arrival_price')), 0, output_field=FloatField()))['all'],
        'farqi_dollar_arrival_price':item.aggregate(all=Coalesce(Sum((F('quantity')-F('old_quantity'))*F('dollar_arrival_price')), 0, output_field=FloatField()))['all'],
    }
    
    context = {
        'item': item,
        'totals':totals,
    }
    return render(request, 'revision_complate_items.html', context)

def revision_add(request):
    date = request.POST.get('date')
    user_profile = request.POST.get('user_profile')
    filial = request.POST.get('filial')
    comment = request.POST.get('comment')
    rev=Revision.objects.create(
        date=date,
        user_profile_id=user_profile,
        filial_id=filial,
        comment=comment,
    )
    return redirect('revision_detail', rev.id)



def revision_detail(request, id):
    revision = Revision.objects.select_related('filial').get(id=id)
    item = RevisionItems.objects.filter(revision=revision)
    products = ProductFilial.objects.filter(filial=revision.filial).select_related('filial')

    product_ids = products.values_list('id', flat=True)

    som_bring_prices = {
        b.product_id: b for b in ProductBringPrice.objects.filter(
            product_id__in=product_ids,
            valyuta__is_som=True,
        ).order_by('product_id', '-id')
    }
    dollar_bring_prices = {
        b.product_id: b for b in ProductBringPrice.objects.filter(
            product_id__in=product_ids,
            valyuta__is_dollar=True,
        ).order_by('product_id', '-id')
    }
    data = []
    for i in products:
        bring_price_som = som_bring_prices.get(i.id)
        bring_price_dollar = dollar_bring_prices.get(i.id)
        dt = {
            'id': i.id,
            'name': i.name,
            'quantity': i.quantity,
            'som_kelish_narx': bring_price_som.price if bring_price_som else 0,
            'dollar_kelish_narx': bring_price_dollar.price if bring_price_dollar else 0,
        }
        data.append(dt)

    valyuta=Valyuta.objects.all()
    totals = []
    for val in valyuta:
        dtt = {
            'id':val.id,
            'name':val.name,
            'total':item.aggregate(all=Coalesce(Sum((F('quantity')-F('old_quantity'))), 0, output_field=FloatField()))['all'],
        }
        totals.append(dtt)
    context = {
        'revision': revision,
        'product': data,
        'price_type':PriceType.objects.filter(is_activate=True),
        'valyuta':valyuta,
        'item':item,
        'totals':totals,
        'totals_quantity':item.aggregate(all=Coalesce(Sum(F('quantity')-F('old_quantity')), 0, output_field=FloatField()))['all'],
    }
    return render(request, 'revision_detail.html', context)


def list_product_price_revision(request):
    data = json.loads(request.body)
    result = []

    for item in data:
        product_id = item['id']
        old_quantity = item['old_quantity']
        quantity = item['quantity']
        if quantity == old_quantity or quantity == 0:
            result.clear()
        elif quantity > old_quantity:
            plus = quantity - old_quantity
            for val in Valyuta.objects.all():   
                price = ProductBringPrice.objects.filter(product_id=product_id, valyuta=val).last()
                if price:
                    dt = {
                            'id': val.id,
                            'plus_summa': price.price * plus,
                            'minus_summa': 0,
                        }
                    result.append(dt)
        elif quantity < old_quantity:
            minus = old_quantity - quantity
            for val in Valyuta.objects.all():   
                price = ProductBringPrice.objects.filter(product_id=product_id, valyuta=val).last()
                if price:
                    dt = {
                            'id': val.id,
                            'plus_summa': 0,
                            'minus_summa': price.price * minus,
                        }
                    result.append(dt)
    print(result)
    return JsonResponse({'data': result})

def revision_one_item_add(request, id):
    data = json.loads(request.body)
    revision = Revision.objects.get(id=id)
    for i in data:
        obj, created = RevisionItems.objects.get_or_create(
            revision=revision,
            product_id=i['id'],
        )
        obj.quantity+=i['quantity']
        obj.old_quantity=i['old_quantity']
        obj.som_arrival_price=i['som_arrival_price']
        obj.dollar_arrival_price=i['dollar_arrival_price']
        obj.save()
    return JsonResponse({'data':True})

def revision_one_item_del(request, id):
    product_id = request.POST.get('product_id')
    RevisionItems.objects.get(revision_id=id,product_id=product_id).delete()
    return JsonResponse({'data':True})

def revision_item_add(request, id):
    data = json.loads(request.body)
    revision = Revision.objects.get(id=id)
    for i in data:
        obj, created = RevisionItems.objects.get_or_create(
            revision=revision,
            product_id=i['id'],
        )
        obj.quantity+=i['quantity']
        obj.old_quantity=i['old_quantity']
        obj.som_arrival_price=i['som_arrival_price']
        obj.dollar_arrival_price=i['dollar_arrival_price']
        obj.save()
    revision.status = 2
    revision.save()
    return redirect('reviziya')


def revison_complate(request, id):
    revision = Revision.objects.get(id=id)
    item = RevisionItems.objects.filter(revision=revision)
    for i in item:
        i.product.quantity = i.quantity 
        i.product.save()
    revision.is_completed = True
    revision.save()
    return redirect(request.META['HTTP_REFERER'])
    

def measurement_type_list(request):
    mesur = MeasurementType.objects.filter(is_active=True)
    context = {
        'mesur':mesur
    }
    return render(request, 'measurement_type_list.html', context)

def measurement_type_add(request):
    name = request.POST.get('name')
    code = request.POST.get('code')
    MeasurementType.objects.create(name=name, code=code)
    return redirect(request.META['HTTP_REFERER'])

def measurement_type_edit(request,id):
    name = request.POST.get('name')
    code = request.POST.get('code')

    valyuta = MeasurementType.objects.get(id=id)
    valyuta.name=name
    valyuta.code=code
    valyuta.save()
    return redirect(request.META['HTTP_REFERER'])