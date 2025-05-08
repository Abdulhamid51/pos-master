from .viewsets import *
from django.urls import path
from .mobilViewset import register, login, teritory_apiview, region_apiview

urlpatterns = [
    path('product_count_edit', product_count_edit, name='product_count_edit'),
    path('customer_debt_edit', customer_debt_edit, name='customer_debt_edit'),
    path('null_product_number', null_product_number, name='null_product_number'),
    path('region/', region_apiview, name='region_apiview'),
    path('teritory/', teritory_apiview, name='teritory_apiview'),
    path('debtor_debt_edit/', debtor_debt_edit, name='debtor_debt_edit'),
    path('prod_fil/', prod_list),
    path('prod_filial_list/', product_filial_list),
    path('chiqim_add/', chiqim_add),
    path('kirim_add/', kirim_add),

	# path('login', login)
]

from .views import all_day_sum_employee

# print('aaa')
# all_day_sum_employee()