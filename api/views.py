from datetime import datetime, timedelta
from django.db.models import Sum, F
from django.db.models.functions import Cast, Coalesce
from api.models import UserProfile, AllDaySumEmployee, Cart, Chiqim, FlexPrice
import calendar



# def all_day_sum_employee():
#     today = datetime.now()
#     befor_day = today - timedelta(days=1)
#     day = befor_day.strftime('%Y-%m-%d')
#     for use in UserProfile.objects.filter(daily_wage=False, staff=3):
#         obj, created = AllDaySumEmployee.objects.get_or_create(user=use, date=day)
#         summa_cart = FlexPrice.objects.filter(user_profile=use, sana=day, is_status=True).distinct().aggregate(all=Coalesce(Sum('total'), 0))['all']
#         payment_sum = Chiqim.objects.filter(user_profile=use, qachon__date=day).aggregate(all=Coalesce(Sum('qancha_som'), 0))['all']
#         day_count = calendar.monthrange(befor_day.year, befor_day.month)[1]
#         fix_day_sum = round(float(use.fix_price//day_count), 2)
#         izox =  Chiqim.objects.filter(user_profile=use, qachon__date=day).last()
        
#         if FlexPrice.objects.filter(user_profile=use, sana=day, is_status=True):
#             obj.fix = fix_day_sum
#             after_summ = float(summa_cart-use.after)

#             if  summa_cart > use.after:
#                 obj.flex = after_summ
#                 obj.rest=float(fix_day_sum+after_summ)
#                 obj.summa=float(fix_day_sum+after_summ)
#             else:
#                 obj.rest=float(fix_day_sum)
#                 obj.summa=float(fix_day_sum)

#         for status in FlexPrice.objects.filter(user_profile=use, sana=day):
#             obj.is_status=status.is_status

#         if izox:
#             obj.izox=izox.izox

#         obj.pay = payment_sum

#         obj.save()

import logging

def all_day_sum_employee():
    logger = logging.getLogger('cronjobs')
    logger.info("all_day_sum_employee funksiyasi ishga tushdi")

    # today = datetime.now()
    today = datetime.strptime('2024-12-13', '%Y-%m-%d')
    befor_day = today - timedelta(days=1)
    day = befor_day.strftime('%Y-%m-%d')
    for i in UserProfile.objects.filter(staff__in=[3, 6]):
        i.refresh_total(befor_day)
    for use in UserProfile.objects.filter(daily_wage=False, staff__in=[3, 6]):
        obj, created = AllDaySumEmployee.objects.get_or_create(user=use, date=day)
        summa_cart = FlexPrice.objects.filter(user_profile=use, sana=day, is_status=True).distinct().aggregate(all=Coalesce(Sum('total'), 0))['all']
        payment_sum = Chiqim.objects.filter(user_profile=use, qachon__date=day).aggregate(all=Coalesce(Sum('qancha_som'), 0))['all']
        day_count = calendar.monthrange(befor_day.year, befor_day.month)[1]
        fix_day_sum = round(float(use.fix_price//day_count), 2)
        izox =  Chiqim.objects.filter(user_profile=use, qachon__date=day).last()
        
        obj.quantity=summa_cart
        obj.flex_price=use.flex_price
        if FlexPrice.objects.filter(user_profile=use, sana=day, is_status=True):
            obj.fix = fix_day_sum
            after_summ = float(summa_cart-use.after)

            if summa_cart > use.after:
                obj.flex = after_summ*float(use.flex_price)
                obj.rest=float(fix_day_sum+(after_summ*float(use.flex_price)))
                obj.summa=float(fix_day_sum+(after_summ*float(use.flex_price)))
            else:
                obj.rest=float(fix_day_sum)
                obj.summa=float(fix_day_sum)

        for status in FlexPrice.objects.filter(user_profile=use, sana=day):
            obj.is_status=status.is_status

        if izox:
            obj.izox=izox.izox

        obj.pay = payment_sum

        obj.save()
        logger.info("Funksiya muvaffaqiyatli tugadi")


# all_day_sum_employee()
# print('aaaa')
# for i in Cart.objects.filter(date__date=datetime.now().date()):
#     print(i)
#     i.save()



from .models import *
def add_daliy_rests():
    day = datetime.datetime.now().date()

    ProductFilialDaily.objects.filter(date=day).delete()
    DebtorDaily.objects.filter(date=day).delete()
    DeliverDaily.objects.filter(date=day).delete()
    KassaDaily.objects.filter(date=day).delete()

    for i in ProductFilial.objects.all():
        new = ProductFilialDaily.objects.create(rest=i.quantity, obyekt=i, date=day)
    
    for i in Debtor.objects.all():
        new = DebtorDaily.objects.create(rest=i.som, obyekt=i, date=day)

    for i in Deliver.objects.all():
        new = DeliverDaily.objects.create(rest=i.som, obyekt=i, date=day)

    for i in KassaMerge.objects.filter(is_active=True):
        new = KassaDaily.objects.create(kassa_merge=i, summa=i.summa, valyuta=i.valyuta, date=day)
    
# print(UserProfile.objects.all())
# add_daliy_rests()


# RejaChiqim.objects.all().delete()


# for i in ProductFilial.objects.all():


# import json

# data = []

# for product in ProductFilial.objects.all():
#     item = {
#         "id": product.id,
#         "deliver": list(product.deliver.values_list('id', flat=True))[0]  # faqat id lar ro'yxati
#     }
#     data.append(item)

# # JSON faylga yozish
# with open("test.json", "w", encoding='utf-8') as f:
#     json.dump(data, f, ensure_ascii=False, indent=4)
