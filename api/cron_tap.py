from datetime import datetime, timedelta
from django.db.models import Sum, F,FloatField
from django.db.models.functions import Cast, Coalesce
from api.models import UserProfile, AllDaySumEmployee, Cart, Chiqim, FlexPrice, OneDayPice
import calendar
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "domstroy.settings")
django.setup()

# def all_day_sum_employee():
#     today = datetime.now()
#     befor_day = today - timedelta(days=2)
#     day = befor_day.strftime('%Y-%m-%d')
#     for use in UserProfile.objects.filter(daily_wage=False, staff=3):
#         obj, created = AllDaySumEmployee.objects.get_or_create(user=use, date=day)
#         summa_cart = FlexPrice.objects.filter(user_profile=use, sana=day, is_status=True).distinct().aggregate(all=Coalesce(Sum('total'), 0))['all']
#         payment_sum = Chiqim.objects.filter(user_profile=use, qachon__date=day).aggregate(all=Coalesce(Sum('qancha_som'), 0))['all']
#         day_count = calendar.monthrange(befor_day.year, befor_day.month)[1]
#         fix_day_sum = round(float(use.fix_price//day_count), 2)
#         izox =  Chiqim.objects.filter(user_profile=use, qachon__date=day).last()
#         after_sum = 0
#         obj.pay = payment_sum
#         if  summa_cart > use.after:
#           if FlexPrice.objects.filter(user_profile=use, sana=day, is_status=True):
#             obj.fix = fix_day_sum
#             obj.rest=float(fix_day_sum+after_sum)
#             obj.summa=float(fix_day_sum+after_sum-payment_sum)
#         else:
#             obj.summa-=float(payment_sum)

#         for i in AllDaySumEmployee.objects.filter(user=use, is_status=True).order_by('date'):
#             obj.rest+=i.rest
#             obj.summa+=i.summa
        
#         for i in AllDaySumEmployee.objects.filter(user=use).order_by('date'):
#             obj.summa-=i.pay

#         for status in FlexPrice.objects.filter(user_profile=use, sana=day):
#             obj.is_status=status.is_status

#         if izox:
#             obj.izox=izox.izox
#         obj.flex = after_sum
#         obj.save()


def all_day_sum_employee():
    # today = datetime.now()
    today = datetime.strptime('2024-06-27')
    befor_day = today - timedelta(days=1)
    day = befor_day.strftime('%Y-%m-%d')
    for use in UserProfile.objects.filter(daily_wage=False, staff=3, id__in=11):
        print('bbbb')
        obj, created = AllDaySumEmployee.objects.get_or_create(user=use, date=day)
        summa_cart = FlexPrice.objects.filter(user_profile=use, sana=day, is_status=True).distinct().aggregate(all=Coalesce(Sum('total'), 0))['all']
        payment_sum = Chiqim.objects.filter(user_profile=use, qachon__date=day).aggregate(all=Coalesce(Sum('qancha_som'), 0))['all']
        day_count = calendar.monthrange(befor_day.year, befor_day.month)[1]
        fix_day_sum = round(float(use.fix_price//day_count), 2)
        izox =  Chiqim.objects.filter(user_profile=use, qachon__date=day).last()
        
        if FlexPrice.objects.filter(user_profile=use, sana=day, is_status=True):
            obj.fix = fix_day_sum
            after_summ = float(summa_cart-use.after)

            if  summa_cart > use.after:
                obj.flex = after_summ*use.flex_price
                print(obj.flex)
                obj.rest=float(fix_day_sum+(after_summ*use.flex_price))
                obj.summa=float(fix_day_sum+(after_summ*use.flex_price))
            else:
                obj.rest=float(fix_day_sum)
                obj.summa=float(fix_day_sum)

        for status in FlexPrice.objects.filter(user_profile=use, sana=day):
            obj.is_status=status.is_status

        if izox:
            obj.izox=izox.izox

        obj.pay = payment_sum

        obj.save()

# all_day_sum_employee()
# print('aaa')


def all_day_sum_one_day():
    today = datetime.now()
    befor_day = today - timedelta(days=1)
    day = befor_day.strftime('%Y-%m-%d')
    for use in UserProfile.objects.filter(daily_wage=True, staff__in=[3, 6]):
        obj, created = AllDaySumEmployee.objects.get_or_create(user=use, date=day)
        payment_sum = Chiqim.objects.filter(user_profile=use, qachon__date=day).aggregate(all=Coalesce(Sum(F('qancha_som')+F('plastik')), 0 ,output_field=FloatField()))['all']
        izox =  Chiqim.objects.filter(user_profile=use, qachon__date=day).last()
        for i in OneDayPice.objects.filter(user_profile=use, sana=day):
            obj.fix=i.one_day_price
            obj.pay=payment_sum
            obj.rest=float(i.one_day_price)-payment_sum
            obj.is_status=i.is_status
        if izox:
            obj.izox=izox.izox
        obj.save()


if __name__ == "__main__":
    all_day_sum_employee()
    all_day_sum_one_day()


# from api.cron_tap import all_day_sum_one_day
# all_day_sum_one_day()