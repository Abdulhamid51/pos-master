from rest_framework import routers
from .mobilViewset import *

router = routers.DefaultRouter()

router.register('cart', MCartViewset, basename='mcart')
router.register('product', ProductFilialViewset, basename='mobil-product')
router.register('banner', BannerViewset, basename='banner')
router.register('order', MOrderViewset, basename='morder')
router.register('debtor', NewDebtorViewSet, basename='mobil-debtor')
router.register('debtor2', DesktopDebtorViewSet, basename='desktop-debtor')
router.register('order2', OrderDesktopViewSet, basename='desktop-order')
