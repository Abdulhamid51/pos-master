from rest_framework import routers
from .mobilViewset import *

router = routers.DefaultRouter()

router.register('cart', MCartViewset)
router.register('product', ProductFilialViewset)
router.register('banner', BannerViewset)
router.register('order', MOrderViewset)
router.register('debtor', NewDebtorViewSet)
router.register('debtor2', DesktopDebtorViewSet)
router.register('order2', OrderDesktopViewSet)