from rest_framework.routers import DefaultRouter
from .viewsets import *
from .mobilViewset import *

router = DefaultRouter()

# router.register('token', TokenViewset)  # Token uchun basename kerak emas hozircha

router.register('pricetype', PriceTypeSerializerViewset, basename='pricetype')
router.register('productpricetype', ProductPriceTypeSerializerViewset, basename='productpricetype')
router.register('userprofile', UserProfileViewset, basename='userprofile')
router.register('filial', FilialViewset, basename='filial')
router.register('groups', GroupsViewset, basename='groups')
router.register('deliver', DeliverViewset, basename='deliver')
router.register('products', Product_FilialViewset, basename='products')
router.register('productfilial', ProductFilialViewsets, basename='productfilial')
router.register('recieve', RecieveViewset, basename='recieve')
router.register('recieveitem', RecieveItemViewset, basename='recieveitem')
router.register('faktura', FakturaViewset, basename='faktura')
router.register('fakturaitem', FakturaItemViewset, basename='fakturaitem')
router.register('shop', ShopViewset, basename='shop')
router.register('cart', CartViewset, basename='cart')
router.register('debtor', DebtorViewset, basename='debtor')
# router.register('debthistory', DebtHistoryViewset)  # Izohga olingan
router.register('debt', DebtViewset, basename='debt')
router.register('payhistory', PayHistoryViewset, basename='payhistory')
router.register('cartdebt', CartDebtViewset, basename='cartdebt')
router.register('returnproduct', ReturnProductViewset, basename='returnproduct')
router.register('changeprice', ChangePriceViewset, basename='changeprice')
router.register('changepriceitem', ChangePriceItemViewset, basename='changepriceitem')
router.register('returnproducttodeliver', ReturnProductToDeliverViewset, basename='returnproducttodeliver')
router.register('returnproducttodeliveritem', ReturnProductToDeliverItemViewset, basename='returnproducttodeliveritem')
router.register('filial-expense', FilialExpenseViewSet, basename='filial-expense')
router.register('filial-expense-category', FilialExpenseCategoryViewSet, basename='filial-expense-category')
router.register('cashbox-receive', CashboxReceiveViewSet, basename='cashbox-receive')
router.register('product-category', ProductCategoryViewset, basename='product-category')
router.register('category', CategoryViewset, basename='category')
router.register('payments_desktop', PaymentDebtorViewSet, basename='payments_desktop')
router.register('payments', PayCheckerViewSet, basename='payments')
router.register('payment-filter', PayCheckerStatus, basename='payment-filter')
router.register('mcart', MCartViewset, basename='mcart')
router.register('desktop_kassa_add', DesktopKassaViewSet, basename='desktop_kassa_add')
router.register('desctopchiqim', DesctopChiqimViewset, basename='desctopchiqim')
router.register('chiqim_turi', ChiqimTuriViewset, basename='chiqim_turi')
