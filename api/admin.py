from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import *
from import_export.admin import ExportActionMixin, ImportExportModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered


admin.site.site_header = "Bordo Admin Panel"
admin.site.site_title = "Bordo API"
admin.site.index_title = "Bordo API"

admin.site.unregister(Group)
admin.site.register(Kamomad)
admin.site.unregister(User)
admin.site.register(MoneyCirculation)

@admin.register(User) 
class EmployeeAdmin(UserAdmin): 
    list_display = ['id', 'username', 'first_name', 'last_name',] 
    # fieldsets = ( 
    #     (None, {'fields': ('username', 'password')}), 
    #     (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}), 
    #     (_('Permissions'), { 
    #         'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'), 
    #     }), 
    #     (_('Extra'), {'fields': ('phone', 'type', 'tegirmon', 'extra_tegirmon', 'order_number', 'firebase_token', 'factory')}), 
    #     (_('Important dates'), {'fields': ('last_login', 'date_joined')}), 
    # )

admin.site.register(PayChecker)

@admin.register(OneDayPice)
class OneDayPiceAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id', 'user_profile', 'sana', 'one_day_price')
    list_filter = ['user_profile', 'sana']
    date_hierarchy = 'sana'
    

@admin.register(FlexPrice)
class FlexPriceAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id', 'sana','total', 'summa_fex')
    date_hierarchy = 'sana'

    def shop_date(self, obj):
        return obj.sana
    
admin.site.register(MobilPayment)



admin.site.register(MobilUser)
admin.site.register(SekretKey)
admin.site.register(MyOwnToken)
admin.site.register(Banner)
admin.site.register(Yalpi_savdo)
admin.site.register(Valyuta)
admin.site.register(Contract)
admin.site.register(NDS)
admin.site.register(WriteOff)
admin.site.register(WriteOffItem)
admin.site.register(ExternalIncomeUser)
admin.site.register(ExternalIncomeUserPayment)
admin.site.register(KassaMerge)
admin.site.register(CustomerDebt)

@admin.register(AllDaySumEmployee)
class AllDaySumEmployeeAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'fix','flex', 'pay', 'rest', 'summa', 'izox', 'is_status')
    list_filter = ['user', 'date']
    date_hierarchy = 'date'

@admin.register(DesktopKassa)
class DesktopKassaAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id', 'kassa_name', 'desktop_id','operation_name', 'qoldik', 'summa', 'yangi_qoldik', 'date_time')
    search_fields = ['desktop_id']

@admin.register(DeliverPaymentsAll)
class DeliverPaymentsAllAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id', 'user', 'received_total', 'gave_total', 'return_total', 'left', 'comment', 'date', 'check_comment',)
    list_filter = ['deliverpayments']
    date_hierarchy = 'date'

@admin.register(DeliverPayments)
class DeliverPaymentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'deliver', 'check_comment')
    list_filter = ['deliver']
    

@admin.register(CashboxReceive)
class CashboxReceiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'filial', 'kassa_sum_old', 'total_sum', 'kassa_sum_new', 'currency')
    list_filter = ['filial']
    date_hierarchy = 'created_at'
    
    
@admin.register(FilialExpense)
class FilialExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'filial', 'category', 'subcategory', 'kassa_sum_old', 'total_sum', 'kassa_sum_new', 'currency')
    list_filter = ['filial']
    date_hierarchy = 'created_at'


@admin.register(MOrder)
class MOrderProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'total')

@admin.register(Telegramid)
class TelegramidProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'telegram_id')

@admin.register(MCart)
class MCartProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'price', 'status')

# admin.site.register(Groups)


class TokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'password', 'first_name', 'last_name', 'phone', 'filial')
    # list_display = ('id', 'username', 'password', 'first_name', 'last_name', 'phone', 'filial')


@admin.register(Groups)
class GroupsAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Pereotsenka)
class PereotsenkaAdmin(admin.ModelAdmin):
    list_display = ('id', 'filial', 'som', 'dollar', 'date')
    list_filter = ('id', 'filial', 'som', 'dollar', 'date')
    date_hierarchy = 'date'


@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address')


@admin.register(Deliver)
class DeliverAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone1', 'phone2', 'som', 'dollar', 'difference')


@admin.register(DesktopChiqim)
class DesktopChiqimAdmin(admin.ModelAdmin):
    list_display = ('id', 'qayerga', 'qancha_som', 'qancha_dol', 'plastik', 'qancha_hisob_raqamdan', 'izox', 'qachon', 'user_profile', 'is_approved')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'som')


@admin.register(PriceType)
class PriceTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')



@admin.register(ProductPriceType)
class ProductPriceTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'product', 'price', 'price_dollar']
    list_filter = ('type', 'product__group', 'product')
    search_fields = ['type__name', 'product__group__name', 'product__name']


@admin.register(ProductFilial)
class ProductFilialAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id', 'category', 'name', 'som', 'dollar', 'quantity', 'filial', 'barcode', 'image', 'distributsiya', 'category')
    search_fields = ('id', 'name', 'som', 'dollar', 'quantity', 'filial__name', 'barcode')
    list_filter = ('filial',)
    


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'debtor', 'desktop_id', 'naqd_som', 'call_center', 'all_count', 'naqd_dollar', 'plastik', 'click', 'nasiya_som', 'nasiya_dollar', 'transfer', 'skidka_som', 'skidka_dollar', 'date', 'saler', 'filial',)
    search_fields = ('id', 'debtor__fio', 'desktop_id')
    list_filter = ('filial', 'saler', 'debtor')
    date_hierarchy = 'date'

    def all_count(self, obj):
        return Cart.objects.select_related('shop', 'shop__saler').filter(shop=obj).distinct().aggregate(all=Coalesce(Sum('quantity'), 0))['all']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'product', 'quantity', 'bring_price', 'price', 'foyda', 'total', 'date', 'shop_date', 'skidka_total')
    search_fields = ('id', 'product__name', 'quantity', 'total', 'shop__id')
    list_filter = ["shop__debtor"]
    date_hierarchy = 'shop__date'

    def shop_date(self, obj):
        return obj.shop.date
    
    def foyda(self, obj):
        return "{:,}".format(obj.foyda)
    



@admin.register(Recieve)
class RecieveAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'som', 'dollar', 'status', 'date')
    search_fields = ('id', 'name', 'som', 'dollar', 'status', 'date')
    date_hierarchy = 'date'


@admin.register(RecieveItem)
class RecieveItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'recieve', 'product', 'som', 'dollar', 'kurs', 'quantity')
    search_fields = ('id', 'som', 'dollar', 'kurs', 'quantity', 'product__name')


@admin.register(Faktura)
class FakturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'som', 'dollar', 'filial', 'date', 'status', 'difference_som', 'difference_dollar')
    search_fields = ('id', 'som', 'dollar', 'filial', 'date', 'status', 'difference_som', 'difference_dollar')
    date_hierarchy = 'date'
    list_filter = ('filial', 'status')


@admin.register(FakturaItem)
class FakturaItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'faktura', 'product', 'som', 'dollar', 'quantity', 'barcode')
    search_fields = ('id', 'faktura', 'product', 'som', 'dollar', 'quantity', 'barcode')
    list_filter = ('faktura',)


@admin.register(Debtor)
class DebtorAdmin(admin.ModelAdmin):
    list_display = ('id', 'fio', 'phone1', 'phone2', 'som', 'dollar', 'difference', 'teritory', 'agent', 'lan', 'lat')
    search_fields = ('id', 'fio', 'phone1', 'phone2', 'som', 'dollar', 'difference')
    
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number', 'is_active')
    search_fields = ('id', 'name')

@admin.register(Teritory)
class TeritoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'region', 'name', 'number', 'is_active')
    search_fields = ('id', 'region', 'name')


# @admin.register(DebtHistory)
# class DebtHistoryAdmin(admin.ModelAdmin):
#     list_display = ('id', 'debtor', 'product', 'debt_quan', 'pay_quan', 'debt', 'pay', 'difference')
#     search_fields = ('id', 'debtor', 'product', 'debt_quan', 'pay_quan', 'debt', 'pay', 'difference')
#     list_filter = ('debtor',)


@admin.register(PayHistory)
class PayHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'debtor', 'desktop_id', 'som', 'dollar', 'date')
    search_fields = ('id', 'debtor','som', 'dollar', 'date')
    list_filter = ('debtor',)
    date_hierarchy = 'date'


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('id', 'debtor', 'shop', 'date', 'return_date')
    search_fields = ('id', 'debtor', 'shop')
    list_filter = ('debtor',)


@admin.register(CartDebt)
class CartDebtAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'debtor', 'product', 'price', 'given_quan', 'total', 'return_quan', 'return_sum', 'debt_quan', 'debt_sum',
        'difference')
    search_fields = (
        'id', 'debtor', 'product', 'price', 'given_quan', 'total', 'return_quan', 'return_sum', 'debt_quan', 'debt_sum',
        'difference')


@admin.register(ReturnProduct)
class ReturnProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'return_quan', 'som', 'difference', 'date')
    search_fields = ('id', 'product', 'return_quan', 'som', 'difference', 'date')
    date_hierarchy = 'date'

@admin.register(ChangePrice)
class ChangePriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'filial', 'date')
    search_fields = ('id', 'filial', 'date')
    date_hierarchy = 'date'

@admin.register(ChangePriceItem)
class ChangePriceItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'changeprice', 'product', 'old_som', 'old_dollar', 'new_som', 'new_dollar', 'quantity')
    search_fields = ('id', 'changeprice', 'product', 'old_som', 'old_dollar', 'new_som', 'new_dollar', 'quantity')


@admin.register(ReturnProductToDeliver)
class ReturnProductToDeliverAdmin(admin.ModelAdmin):
    list_display = ('id', 'deliver', 'som', 'dollar', 'date')
    date_hierarchy = 'date'


@admin.register(ReturnProductToDeliverItem)
class ReturnProductToDeliverItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'returnproduct', 'product', 'som', 'dollar', 'quantity')

@admin.register(DebtDeliver)
class DebtDeliverAdmin(admin.ModelAdmin):
    list_display = ('id', 'deliver', 'som', 'dollar', 'date')
    search_fields = ('id', 'deliver', 'som', 'dollar', 'date')
    list_filter = ('deliver',)
    date_hierarchy = 'date'


@admin.register(DeliverPayHistory)
class DeliverPayHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'deliver', 'som', 'dollar', 'date')
    search_fields = ('id', 'deliver', 'som', 'dollar', 'date')
    list_filter = ('deliver',)
    date_hierarchy = 'date'

@admin.register(Kassa)
class KassaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nomi', 'som', 'dollar', 'hisob_raqam', 'plastik')
    list_display_links = ('id', 'nomi', 'som', 'dollar')

@admin.register(ChiqimTuri)
class ChiqimTuriAdmin(admin.ModelAdmin):
    list_display = ('id', 'nomi')
    list_display_links = ('id', 'nomi')

@admin.register(Chiqim)
class ChiqimAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display_links = ('id', 'qayerga', 'qancha_som', 'qancha_dol', 'qachon')
    list_display = ('id', 'qayerga', 'qancha_som', 'qancha_dol', 'qachon', 'deliver')
    list_filter = ['deliver']
    date_hierarchy = 'qachon'

@admin.register(HodimModel)
class HodimModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'ism', 'familya', 'oylik')
    list_display_links = ('id', 'ism', 'familya', 'oylik')

@admin.register(HodimQarz)
class HodimQarzAdmin(admin.ModelAdmin):
    list_display = ('id', 'hodim', 'qancha_som', 'qancha_dol', 'qaytargani_som', 'qaytargani_dol', 'izox', 'qachon', 'tolandi')
    list_display_links = ('id', 'hodim', 'qancha_som', 'qancha_dol', 'qachon')

@admin.register(FilialExpenseCategory)
class FilialExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']
    

@admin.register(OylikTolov)
class OylikTolovAdmin(admin.ModelAdmin):
    list_display = ('id', 'pul', 'sana')
    list_display_links = ('id', 'pul', 'sana')
    
    
@admin.register(Kirim)
class KirimAdmin(admin.ModelAdmin):
    list_display = ('id', 'qancha_som', 'qancha_dol', 'qancha_hisob_raqamdan', 'plastik')
    


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'name', 'image')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image')



@admin.register(ProductFilialDaily)
class ProductFilialDailyAdmin(admin.ModelAdmin):
    list_display = ('id', 'obyekt', 'date', 'rest')



@admin.register(DebtorDaily)
class DebtorDailyAdmin(admin.ModelAdmin):
    list_display = ('id', 'obyekt', 'date', 'rest')


@admin.register(DeliverDaily)
class DeliverDailyAdmin(admin.ModelAdmin):
    list_display = ('id', 'obyekt', 'date', 'rest')


@admin.register(KassaDaily)
class KassaDailyAdmin(admin.ModelAdmin):
    list_display = ('id', 'obyekt', 'date')



@admin.register(ChiqimCategory)
class ChiqimCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')



@admin.register(ChiqimSubCategory)
class ChiqimSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')


@admin.register(KassaNew)
class KassaNewAdmin(admin.ModelAdmin):
    list_display = ('id', 'filial', 'is_active', 'is_main', 'name', 'kassa_user')



