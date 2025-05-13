from email.policy import default
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

from django.db.models import Sum, F
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import datetime
from django.db.models.functions import Coalesce
from django.db.models import IntegerField
#from django.contrib.gis.db import models
#from django.contrib.gis.geos import Point
from django.db.models import Manager as GeoManager
from django.core.validators import RegexValidator
from itertools import chain


# class UserCustom(AbstractUser):
#     is_bussines = models.BooleanField(default=False)
#     is_maxsulot_boshkaruvi = models.BooleanField(default=False)
#     is_maxsulot_tahriri = models.BooleanField(default=False)
#     is_taminotchi_qaytuv = models.BooleanField(default=False)
#     is_bugungi_sotuvlar = models.BooleanField(default=False)
#     is_maxsutlo_tahlili = models.BooleanField(default=False)
#     is_analiz_xarajatlar = models.BooleanField(default=False)
#     is_ot_prixod = models.BooleanField(default=False)
#     is_ot_tarix = models.BooleanField(default=False)
#     is_hisobdan_chiqish = models.BooleanField(default=False)
#     is_hisobdan_tarix = models.BooleanField(default=False)
#     is_xodim_kunlik = models.BooleanField(default=False)
#     is_xodim_oylik = models.BooleanField(default=False)
#     is_xodim_mobile = models.BooleanField(default=False)
#     is_xodim_call_center = models.BooleanField(default=False)
#     is_balans_hisobi = models.BooleanField(default=False)
#     is_fin_hisoboti = models.BooleanField(default=False)
#     is_buyurtmalar = models.BooleanField(default=False)
#     is_filial_boshkaruvi = models.BooleanField(default=False)
#     is_kadrlar = models.BooleanField(default=False)
#     is_mijozlar_qarzdorligi = models.BooleanField(default=False)
#     is_mijozlar_tahlili = models.BooleanField(default=False)
#     is_yetkazib beruvchilar = models.BooleanField(default=False)
#     is_ombor_boshkaruvi_ombor = models.BooleanField(default=False)
#     is_ombor_boshkaruvi_qabul = models.BooleanField(default=False)
#     is_ombor_boshkaruvi_ombordan_analiz = models.BooleanField(default=False)
#     is_reyting_maxsulotlar = models.BooleanField(default=False)
#     is_reyting_mijozlar = models.BooleanField(default=False)
#     is_reyting_yetkazib_beruvchilar = models.BooleanField(default=False)
#     is_kassa = models.BooleanField(default=False)
#     is_savdo = models.BooleanField(default=False)
#     is_b2b_savdo = models.BooleanField(default=False)
#     is_kassa_tasdiklanmagan = models.BooleanField(default=False)
#     is_qabul = models.BooleanField(default=False)

class Valyuta(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    is_dollar = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']

class Contract(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    # status_type = [
    #     (1, 'yangi'),
    #     (2, 'yakunlangan'),
    #     (3, 'bekorkilingan'),
    # ]
    # status = models.IntegerField(choices=status_type, default=3)
    is_active = models.BooleanField(default=True)


class NDS(models.Model):
    perecent = models.IntegerField(default=0)

class Yalpi_savdo(models.Model):
    products = models.ForeignKey("api.ProductFilial",on_delete=models.SET_NULL,null=True)
    filial = models.ForeignKey("api.Filial",on_delete=models.SET_NULL,null=True)
    total_sum = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.products} - yalpi:{self.total_sum}"
    



class MobilUser(models.Model):
    phone = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=25)
    username = models.CharField(max_length=200,null=True)
    is_authenticated = models.BooleanField(default=False)
    
    fix_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    flex_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    price_and = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='Oylik ishchi kelmaganda ayriladigon pul')
    after = models.IntegerField(default=0, verbose_name='Flex limit')
       

    def __str__(self):
        return self.phone

    class Meta:
        verbose_name_plural = 'Mobile Users'


class Filial(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    qarz_som = models.IntegerField(default=0)
    qarz_dol = models.IntegerField(default=0)
    savdo_puli_som = models.IntegerField(default=0)
    savdo_puli_dol = models.IntegerField(default=0)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    is_activate = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '2) Filial'


class HodimModel(models.Model):
    ism = models.CharField(max_length=50)
    familya = models.CharField(max_length=50)
    filial = models.ForeignKey(Filial, on_delete=models.SET_NULL, null=True, blank=True)
    oylik = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Hodimlar'

    def __str__(self) -> str:
        return f'{self.ism} {self.familya}'

    def toliq_ism_ol(self):
        return f'{self.ism} {self.familya}'

    
class HodimQarz(models.Model):
    hodim = models.ForeignKey(HodimModel, on_delete=models.CASCADE)
    qancha_som = models.PositiveIntegerField(default=0)
    qancha_dol = models.PositiveIntegerField(default=0)
    qaytargani_som = models.IntegerField(default=0)
    qaytargani_dol = models.IntegerField(default=0)
    izox = models.TextField(null=True, blank=True)
    qaytargandagi_izox = models.TextField(null=True, blank=True)
    tolandi = models.BooleanField(default=False)
    qachon = models.DateTimeField(auto_now_add=True)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self) -> str:
        return self.hodim.toliq_ism_ol()

    def qarzni_tekshir(self):
        
        if self.qancha_dol == self.qaytargani_dol and self.qancha_som == self.qaytargani_som:
            self.tolandi = True
            self.save()

        return 0

    class Meta:
        verbose_name_plural  = "Hodimlar qarzi"


class OylikTolov(models.Model):
    hodim = models.ForeignKey(HodimModel, on_delete=models.CASCADE)
    pul  = models.PositiveIntegerField(blank=False, null=False)
    sana = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.hodim.toliq_ism_ol()


class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    
    staffs = [
        (1, 'director'),
        (2, 'manager'),
        (3, 'saler'),
        (4, 'warehouse'),
        (5, 'agent'),
        (6, 'call_center'),
    ]
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, null=True, blank=True)
    staff = models.IntegerField(choices=staffs, default=3)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)
    
    one_day_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    fix_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    flex_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    price_and = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name='Oylik ishchi kelmaganda ayriladigon pul')
    after = models.IntegerField(default=0, verbose_name='Flex limit')
    daily_wage = models.BooleanField(default=True)
    #own

    is_bussines = models.BooleanField(default=False)
    is_maxsulot_boshkaruvi = models.BooleanField(default=False)
    is_maxsulot_tahriri = models.BooleanField(default=False)
    is_taminotchi_qaytuv = models.BooleanField(default=False)
    is_bugungi_sotuvlar = models.BooleanField(default=False)
    is_maxsutlo_tahlili = models.BooleanField(default=False)
    is_analiz_xarajatlar = models.BooleanField(default=False)
    is_ot_prixod = models.BooleanField(default=False)
    is_ot_tarix = models.BooleanField(default=False)
    is_hisobdan_chiqish = models.BooleanField(default=False)
    is_hisobdan_tarix = models.BooleanField(default=False)
    is_xodim_kunlik = models.BooleanField(default=False)
    is_xodim_oylik = models.BooleanField(default=False)
    is_xodim_mobile = models.BooleanField(default=False)
    is_xodim_call_center = models.BooleanField(default=False)
    is_balans_hisobi = models.BooleanField(default=False)
    is_fin_hisoboti = models.BooleanField(default=False)
    is_buyurtmalar = models.BooleanField(default=False)
    is_filial_boshkaruvi = models.BooleanField(default=False)
    is_kadrlar = models.BooleanField(default=False)
    is_mijozlar_qarzdorligi = models.BooleanField(default=False)
    is_mijozlar_tahlili = models.BooleanField(default=False)
    is_yetkazib_beruvchilar = models.BooleanField(default=False)
    is_ombor_boshkaruvi_ombor = models.BooleanField(default=False)
    is_ombor_boshkaruvi_qabul = models.BooleanField(default=False)
    is_ombor_boshkaruvi_ombordan_analiz = models.BooleanField(default=False)
    is_reyting_maxsulotlar = models.BooleanField(default=False)
    is_reyting_mijozlar = models.BooleanField(default=False)
    is_reyting_yetkazib_beruvchilar = models.BooleanField(default=False)
    is_kassa = models.BooleanField(default=False)
    is_savdo = models.BooleanField(default=False)
    is_b2b_savdo = models.BooleanField(default=False)
    is_kassa_tasdiklanmagan = models.BooleanField(default=False)
    is_qabul = models.BooleanField(default=False)

    is_nds = models.BooleanField(default=False)
    is_kassa_tarixi = models.BooleanField(default=False)


    def refresh_total(self, date):
        if type(date) == str:
            date = date[:10]
        if self.daily_wage == False:
            obj, created = FlexPrice.objects.get_or_create(user_profile=self, sana=date)
            if self.staff == 3:
                obj.total = Cart.objects.select_related('shop', 'shop__saler').filter(shop__saler__staff=3, shop__date__date=date).distinct().aggregate(all=Coalesce(Sum('quantity'), 0))['all']
            obj.save() 
        if self.staff == 6:
            obj, created = FlexPrice.objects.get_or_create(user_profile=self, sana=date)
            obj.total  = Cart.objects.select_related('shop', 'shop__saler').filter(shop__call_center=self.username, shop__date__date=date).distinct().aggregate(all=Coalesce(Sum('quantity'), 0))['all']
            print(obj.total, 'kk')
            obj.save() 

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name_plural = '1) User'



    
class Groups(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '3.1) Group'


class Viloyat(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)


class Deliver(models.Model):
    name = models.CharField(max_length=255)
    viloyat = models.ForeignKey(Viloyat, on_delete=models.CASCADE, blank=True, null=True)
    phone1 = models.CharField(max_length=13)
    phone2 = models.CharField(max_length=13, blank=True, null=True)
    som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)
    difference = models.IntegerField(default=0)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def debts(self):
        all_debts = self.debtdeliver.all().aggregate(Sum('som'))['som__sum']
        all_pays = self.deliverpayhistory.aggregate(Sum('som'))['som__sum']
        return all_debts + all_pays

    class Meta:
        verbose_name_plural = '3.1) Deliver'

class DeliverPaymentsAll(models.Model):
    deliver = models.ForeignKey(Deliver, on_delete=models.PROTECT, blank=True, null=True, related_name='deliverpaymentsall')
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    received_total = models.FloatField(default=0, blank=True, null=True)
    gave_total = models.FloatField(default=0, blank=True, null=True)
    return_total = models.FloatField(default=0, blank=True, null=True)
    left = models.FloatField(default=0, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    check_comment = models.TextField(blank=True, null=True)
    recieve = models.ForeignKey('Recieve', on_delete=models.CASCADE, null=True, blank=True)

    # def save(self, *args, **kwargs):
    #     if 'a' == 'b':
    #         super().save()
    #         PayHistory.objects.create(
    #             deliver_all_payment=self,
    #             comment=self.comment,
                
    #         )
    
    class Meta:
        ordering = ['id']
    

class DeliverPayments(models.Model):
    deliver = models.ForeignKey(Deliver, on_delete=models.PROTECT, blank=True, null=True, related_name='deliverpayments')
    date = models.DateTimeField(default=timezone.now)
    # received_total = models.FloatField(default=0)
    # total = models.FloatField(default=0)
    # gave_total = models.FloatField(default=0)
    # comment = models.TextField(blank=True, null=True)
    # left = models.FloatField(default=0)
    payments = models.ManyToManyField(DeliverPaymentsAll, related_name='deliverpayments', blank=True)
    check_comment = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return str(self.deliver.name)


class DebtDeliver(models.Model):
    deliver = models.ForeignKey(Deliver, on_delete=models.CASCADE, related_name='debtdeliver')
    date = models.DateTimeField(default=timezone.now)
    som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    recieve = models.ForeignKey('Recieve', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.deliver.name

    class Meta:
        verbose_name_plural = 'Deliver Qarzi'

@receiver(post_save, sender=User)
def save_password(sender, instance: User, created, **kwargs):
    if created:
        instance.set_password(instance.password)
        instance.save()



@receiver(post_save, sender=DebtDeliver)
def change_payments_debt(sender, instance, **kwargs):
    payments = DeliverPayments.objects.filter(deliver=instance.deliver).order_by('id')
    if payments.exists():
        payment = payments.last()
    else:
        payment = DeliverPayments.objects.create(deliver=instance.deliver)
        
    payment.deliver = instance.deliver
    deliver = instance.deliver
    recieve = instance.recieve
    # deliver.som += int(instance.som) if instance.som else 0
    # deliver.som += (int(instance.dollar) if instance.dollar else 0) * Course.objects.last().som


    # payment1 = DeliverPaymentsAll.objects.create()
    # payment1.received_total += int(instance.som) if instance.som else 0
    # payment1.received_total += (int(instance.dollar) if instance.dollar else 0) * Course.objects.last().som
    
    
    payment1 = DeliverPaymentsAll.objects.create()
    if recieve:
        payment1.recieve=recieve
    payment1.received_total += float(instance.som) if instance.som else 0
    payment1.received_total += (float(instance.dollar) if instance.dollar else 0) * Course.objects.last().som
    
    
    # deliver.som += payment1.received_total
    payment1.left = deliver.som
    
    payment.payments.add(payment1)
    deliver.save()
    payment1.save()
    payment.save()
    
    # date = datetime.datetime.now()
    # payments = DeliverPayments.objects.filter(date__date=date.date())
    # if payments.exists():
    #     payment = payments.last()
    # else:
    #     payment = DeliverPayments.objects.create()
    
    
    # if instance.som:
    #     payment.received_total = instance.som
    
    # if instance.dollar:
    #     payment.received_total = instance.dollar * Course.objects.last().som
    
    # payments_before = DeliverPayments.objects.filter(id=(int(payment.id)-1))
    # if payments_before.exists():
    #     payment_before = payments_before.last()
    #     if payment_before.left:
    #         payment.total = payment_before.left - payment.received_total
    #     elif payment_before.total:
    #         payment.total = payment_before.total + payment.received_total
    #     else:
    #         payment.total = payment.received_total
    # else:
    #     payment.total = payment.received_total
        
    
    # payment.save()
            


class DeliverPayHistory(models.Model):
    type_pay = (
        ("Naqd", "Naqd"),
        ("Plastik", "Plastik"),
        ("Pul o'tkazish", "Pul o'tkazish")
    )
    deliver = models.ForeignKey(Deliver, on_delete=models.CASCADE, related_name='deliverpayhistory')
    som = models.IntegerField()
    dollar = models.IntegerField()
    turi = models.CharField(max_length=50, choices=type_pay, default="Naqd")
    date = models.DateTimeField(auto_now_add=True)
    kurs = models.FloatField(default=0, blank=True, null=True)
    #new
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    money_circulation = models.ForeignKey('MoneyCirculation', on_delete=models.CASCADE, null=True, blank=True)
    izoh = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.deliver.name

    @property
    def total(self):
        return self.dollar * self.kurs + self.som

    class Meta:
        verbose_name_plural = 'Deliver Tolov Tarixi'


@receiver(post_save, sender=DeliverPayHistory)
def change_payments_pay(sender, instance, **kwargs):
    payments = DeliverPayments.objects.filter(deliver=instance.deliver).order_by('id')
    if payments.exists():
        payment = payments.first()
    else:
        payment = DeliverPayments.objects.create(deliver=instance.deliver)
        
    payment.deliver = instance.deliver
    deliver = instance.deliver
    # deliver.som += int(instance.som) if instance.som else 0
    # deliver.som += (int(instance.dollar) if instance.dollar else 0) * Course.objects.last().som

    payment1 = DeliverPaymentsAll.objects.create(comment=instance.izoh)
    payment1.gave_total += int(instance.som) if instance.som else 0
    payment1.gave_total += (int(instance.dollar) if instance.dollar else 0) * Course.objects.last().som
    
    
    # payment.comment = instance.izoh
    
    deliver.som += payment1.gave_total
    payment1.left = deliver.som
    payment.payments.add(payment1)
    deliver.save()
    payment1.save()
    payment.save()


class Category(models.Model):
    name = models.CharField(max_length=250)
    image = models.FileField(upload_to="product_categories/", null=True, blank=True)

    def __str__(self):
        return self.name

class ProductCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=250)
    image = models.FileField(upload_to="product_categories/", null=True, blank=True)

    def __str__(self):
        return self.name
    
from django.db.models import Value

class ProductFilial(models.Model):
    deliver = models.ManyToManyField(Deliver, related_name='products1', blank=True)
    measure = [
        ('dona', 'dona'),
        ('kg', 'kg'),
        ('litr', 'litr'),
        ('metr', 'metr')
    ]
    name = models.CharField(max_length=255)
    preparer = models.CharField(max_length=255, default="")
    som = models.IntegerField(default=0) #kelish narxi
    sotish_som = models.IntegerField(default=0) #sotish narxi
    dollar = models.IntegerField(default=0)
    sotish_dollar = models.IntegerField(default=0)
    kurs = models.IntegerField(default=0)
    barcode = models.CharField(max_length=255)
    barcode_image = models.ImageField(upload_to="barcode_product/", null=True, blank=True)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    deliver1 = models.ForeignKey(Deliver, on_delete=models.CASCADE, blank=True, null=True)
    measurement = models.CharField(choices=measure, default='dona', max_length=4)
    min_count = models.IntegerField(default=0)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, related_name='filial_product')
    # filial = models.ForeignKey(Filial, on_delete=models.CASCADE, related_name='filial_product')
    quantity = models.IntegerField(default=0)
    start_quantity = models.IntegerField(default=0)
    start_date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    distributsiya = models.IntegerField(default=0)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, blank=True, null=True)
    # date = models.DateField(auto_now_add=True, null=True, blank=True)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.name + " - " + self.barcode
    
    class Meta:
        verbose_name_plural = '3.1) Product Filial'

        


        
    def return_recieves(self, start_date, end_date, deliver_id):
        recieves = RecieveItem.objects.filter(product=self)
        if deliver_id:
            deliver = Deliver.objects.get(id=deliver_id)
            recieves = recieves.filter(recieve__deliver=deliver)
        
        if start_date and end_date:
            recieves = recieves.filter(recieve__date__date__gte=start_date, recieve__date__date__lte=end_date)
        # print(recieves, 'aaa')
        total = recieves.aggregate(Sum('quantity'))['quantity__sum']
        return total if total else 0
    
    def return_carts(self, start_date, end_date, debtor=None):
        carts = Cart.objects.filter(product=self)
        if start_date and end_date:
            carts = carts.filter(shop__date__date__gte=start_date, shop__date__date__lte=end_date)
        if debtor:
            carts = carts.filter(shop__debtor__id=debtor)
        total = carts.aggregate(foo=Coalesce(Sum(F('quantity')), int(0), output_field=IntegerField()))['foo']
        return total if total else 0
    

    # class cart
    def foyda(self, start_date, end_date, debtor=None):
        recieve = RecieveItem.objects.filter(product=self).last()
        carts = Cart.objects.filter(product=self)
        if start_date and end_date:
            carts = carts.filter(shop__date__date__gte=start_date, shop__date__date__lte=end_date)
        if debtor:
            carts = carts.filter(shop__debtor__id=debtor)
        total = carts.aggregate(foo=Coalesce(Sum((F('price') - F('bring_price')) * F('quantity'), output_field=models.FloatField()), Value(0)))['foo']
        # total = carts.aggregate(
        #     foo=Coalesce(Sum((F('price') - F('bring_price')) * F('quantity')),output_field=float()),default=0)['foo']
        return total
    

class Recieve(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    deliver = models.ForeignKey(Deliver, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    som = models.IntegerField(default=0)
    sum_sotish_som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)
    sum_sotish_dollar = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    farq_dollar = models.IntegerField(default=0)
    farq_som = models.IntegerField(default=0)
    is_prexoded = models.BooleanField(default=False)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, null=True, blank=True)
    

    # difference = models.IntegerField(default=0)
    def save(self, *args, **kwargs):
        self.som = sum([i.som * i.quantity for i in self.receiveitem.all()])
        self.sum_sotish_som = sum([i.sotish_som * i.quantity for i in self.receiveitem.all()])
        self.dollar = 0
        self.sum_sotish_dollar = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)
    
    @property
    def kelish_total(self):
        return self.receiveitem.all().aggregate(foo=Sum(F('quantity') * F('som')))['foo']

    @property
    def sotish_total(self):
        return self.receiveitem.all().aggregate(foo=Sum(F('quantity') * F('sotish_som')))['foo']

    @property
    def total_quantity(self):
        return self.receiveitem.all().aggregate(foo=Sum(F('quantity')))['foo']
    
    
    class Meta:
        verbose_name_plural = '4) Recieve'


class RecieveItem(models.Model):
    recieve = models.ForeignKey(Recieve, on_delete=models.CASCADE, related_name='receiveitem')
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE, related_name='product_recieves')
    som = models.IntegerField(default=0)
    sotish_som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)
    sotish_dollar = models.IntegerField(default=0)
    kurs = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    old_prices = models.JSONField(blank=True, null=True)
    old_quantity = models.IntegerField(default=0)
    old_sotish_som = models.IntegerField(default=0)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.product.name

    @property
    def total_som(self):
        return self.som *self.quantity
    
    
    @property
    def total_sotish_som(self):
        return self.som *self.quantity
    
    @property
    def pereotsenka_zarar(self):
        total = self.sotish_som - self.old_sotish_som * self.old_quantity
        if total < 0:
            return total
        return 0

    @property
    def pereotsenka_foyda(self):
        total = (self.sotish_som - self.old_sotish_som) * self.old_quantity
        if total > 0:
            return total
        return 0
    
    @property
    def pereotsenka_foyda_types(self):
        data = []
        for prtype in PriceType.objects.all().order_by('id'):
            prtypeproduct = ProductPriceType.objects.filter(type=prtype, product=self.product).last()
            if prtypeproduct:
                price = prtypeproduct.price
            else:
                price = 0
            
            old_price = 0

            if self.old_prices:
                for js in self.old_prices['datas']:
                    if js['name'] == prtype.name:
                        old_price = js['price']

            # old_prtypeproduct = ProductPriceType.objects.filter(type=prtype, product=self.product).last()
            # if prtypeproduct:
            #     price = prtypeproduct.price
            # else:
            #     price = 0
            total = (float(price) - old_price) * self.old_quantity
            dt = {
                'name': prtype.name,
                'total': total if total > 0 else 0
            }
            data.append(dt)
        return data

    
    @property
    def pereotsenka_zarar_types(self):
        data = []
        for prtype in PriceType.objects.all():
            prtypeproduct = ProductPriceType.objects.filter(type=prtype, product=self.product).last()
            if prtypeproduct:
                price = prtypeproduct.price
            else:
                price = 0
            
            old_price = 0
            if self.old_prices:
                for js in self.old_prices['datas']:
                    if js['name'] == prtype.name:
                        old_price = js['price']

            total = (float(price) - old_price) * self.old_quantity
            dt = {
                'name': prtype.name,
                'total': total if total < 0 else 0
            }
            data.append(dt)
        return data


    class Meta:
        verbose_name_plural = '4.1) RecieveItem'




class Faktura(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    difference_som = models.IntegerField(default=0)
    difference_dollar = models.FloatField(default=0)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = '6) Faktura'


class FakturaItem(models.Model):
    name = models.CharField(max_length=255)
    faktura = models.ForeignKey(Faktura, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, blank=True, null=True)
    body_som = models.IntegerField(default=0)
    body_dollar = models.IntegerField(default=0)
    som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    barcode = models.CharField(max_length=255)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name_plural = '6.1) FakturaItem'


class Course(models.Model):
    som = models.IntegerField()

    def __str__(self):
        return str(self.som)
    
    class Meta:
        verbose_name_plural = "Dollar kursi"


class Shop(models.Model):
    desktop_id = models.SlugField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    naqd_som = models.IntegerField(default=0) 
    naqd_dollar = models.IntegerField(default=0)
    plastik = models.FloatField(default=0)
    click = models.PositiveIntegerField(default=0)
    nasiya_som = models.IntegerField(default=0)
    nasiya_dollar = models.IntegerField(default=0)
    transfer = models.IntegerField(default=0)
    skidka_dollar = models.IntegerField(default=0)
    skidka_som = models.IntegerField(default=0)
    kurs = models.IntegerField(default=0)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    saler = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='seller_orders')
    call_center = models.CharField(max_length=200, blank=True, null=True)
    # call_center = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='call_center_orders')
    debtor = models.ForeignKey("Debtor", on_delete=models.CASCADE, blank=True, null=True, related_name='debtor_shops')
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE, related_name='shop', blank=True, null=True)
    
    #qarzni qaytarish sanasi
    debt_return = models.DateField(null=True, blank=True)

    is_som  = models.BooleanField(default=True)
    is_dollar = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    som_after = models.FloatField(default=0)
    dollar_after = models.FloatField(default=0)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    b2c = models.BooleanField(default=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=True, blank=True)
    type_price = models.ForeignKey('PriceType', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    is_savdo = models.BooleanField(default=True)
    nds_count = models.IntegerField(default=0)
    debt_old = models.IntegerField(default=0)
    debt_new = models.IntegerField(default=0)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_finished:
            obj, created = PayHistory.objects.get_or_create(shop=self, debtor = self.debtor)
            # obj.debtor = self.debtor
            obj.filial = self.filial
            obj.som = self.naqd_som
            obj.dollar = self.naqd_dollar
            obj.click = self.click
            obj.plastik = self.plastik
            obj.currency = self.kurs
            obj.save()
    
    @property
    def model_name(self):
        return 'shop'

    # def save_summas(self):
    #     carts = self.cart.all()
    #     for cart in carts:
    #         if self.is_som:
    #             self.nasiiya_som = cart.price * cart.quantity - self.som

    @property
    def get_model(self):
        return self._meta.model_name

    @property
    def baskets_total_price(self):
        return sum([i.total_price for i in self.cart.all()])

    @property
    def baskets_total_skidka(self):
        return sum([i.skidka for i in self.cart.all()])

    
    @property
    def price_without_skidka(self):
        return self.price + self.skidka_som if self.skidka_som > 0 else self.skidka_dollar
    
    @property
    def total_som(self):
        return self.naqd_som + self.plastik + self.click + (self.dollar * self.kurs)
    
    @property
    def som_nasiya_bilan(self):
        return self.naqd_som + self.plastik + self.click + self.nasiya_som + (self.dollar * self.kurs)
    
    @property
    def total_dollar(self):
        return self.dollar + (self)

    @property
    def som(self):
        return self.naqd_som + self.nasiya_som - self.skidka_som
    
    @property
    def dollar(self):
        return self.naqd_dollar + self.nasiya_dollar - self.skidka_dollar
    
    @property
    def product_price(self):
        som = 0
        for i in self.cart.all():
            som += i.price * i.quantity
        return som
    
    @property
    def product_count(self):
        return sum([i.quantity for i in self.cart.all()])

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = '5) Shop'


class Cart(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True, related_name='cart')
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE, related_name='cart', blank=True, null=True)
    bring_price = models.FloatField(default=0)
    after_cart = models.FloatField(default=0)
    price_without_skidka = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    total = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    applied = models.BooleanField(default=False)
    skidka_total = models.IntegerField(default=0)

    @property
    def foyda(self):
        return self.quantity * (self.price - self.bring_price)
    
    @property
    def skidka(self):
        return (self.price_without_skidka -  self.price) * self.quantity
    
    @property
    def total_price(self):
        return self.quantity * self.price

    @property
    def for_call_center(self):
        if self.shop.call_center:
            print(self.shop.call_center)
            call_center = UserProfile.objects.filter(username=self.shop.call_center).last()
            print(call_center)
            if call_center:
                return call_center.flex_price * self.quantity
            # return 0
        return 0

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        employes = UserProfile.objects.filter(staff__in=[3,6],  daily_wage=False)
        
        for i in employes:    
            obj, created = FlexPrice.objects.get_or_create(user_profile=i, sana=self.date.date())
            if i.staff == 3:
                obj.total = Cart.objects.filter(shop__saler__staff=3, date__date=self.date.date()).aggregate(all=Coalesce(Sum('quantity'), 0))['all']
            if i.staff == 6:
                print(Cart.objects.filter(shop__call_center=i.username, date__date=self.date.date()), 'ooo')
                obj.total = Cart.objects.filter(shop__call_center=i.username, date__date=self.date.date()).aggregate(all=Coalesce(Sum('quantity'), 0))['all']
                print(obj.total, 'eeee')
            
            obj.save()
        
    
    def delete(self, *args, **kwargs):
        self.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        try:
            return self.product.name
        except:
            return 'Deleted Product'

    class Meta:
        verbose_name_plural = '5.1) Cart'


class DebtorType(models.Model):
    name = models.CharField(max_length=40)
    number = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Debtor(models.Model):
    desktop_id = models.IntegerField(blank=True, null=True)
    type = models.ForeignKey(DebtorType, on_delete=models.PROTECT, blank=True, null=True)
    teritory = models.ForeignKey('Teritory', on_delete=models.PROTECT, blank=True, null=True)
    agent = models.ForeignKey('MobilUser', on_delete=models.PROTECT, blank=True, null=True, related_name='debtors')
    image = models.FileField(upload_to='debtor_images/', blank=True, null=True)
    fio = models.CharField(max_length=255)
    phone1 = models.CharField(max_length=13)
    phone2 = models.CharField(max_length=13, blank=True, null=True)
    som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)

    start_som = models.IntegerField(default=0)
    start_dollar = models.IntegerField(default=0)

    start_date = models.DateTimeField(default=timezone.now())

    difference = models.IntegerField(default=0)
    lan = models.FloatField(default=0)
    lat = models.FloatField(default=0)
    #new fields
    debt_return = models.DateField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    inn = models.CharField(max_length=450, blank=True, null=True)
    company = models.CharField(max_length=250, blank=True, null=True)
    address = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=True, blank=True)
    
    
    def __str__(self):
        return self.fio

    def save(self, *args, **kwargs):
        if self.phone1 and '+' in self.phone1:
            self.phone1 = self.phone1.replace('+', '')
        
        if self.phone2 and '+' in self.phone2:
            self.phone2 = self.phone2.replace('+', '')
        super().save()
        
        for val in Valyuta.objects.all():
            CustomerDebt.objects.get_or_create(customer=self, valyuta=val)

    def refresh_debt(self):
        customer = self
        pay_history = PayHistory.objects.filter(debtor=customer).order_by('-id')
        shop = Shop.objects.filter(debtor=customer).order_by('-id')
        infos = sorted(chain(pay_history, shop), key=lambda instance: instance.date)
        customer_debts = CustomerDebt.objects.filter(customer=customer)

        for valyuta in Valyuta.objects.all():
            customer_debt = CustomerDebt.objects.filter(valyuta=valyuta).last() or CustomerDebt.objects.create(customer=customer, valyuta=valyuta)
            if customer_debt:
                # Asl summa bilan yangilash
                customer_debt.summa = customer_debt.start_summa
                customer_debt.save()

                # To'lov va xaridlarni yangilash
                for i in infos:
                    if i.valyuta == valyuta:
                        if i._meta.model_name == 'payhistory':
                            i.debt_old = customer_debt.summa
                            if i.type_pay == 1:
                                customer_debt.summa += i.summa
                            else:
                                customer_debt.summa -= i.summa
                            i.debt_new = customer_debt.summa
                        elif i._meta.model_name == 'shop':
                            i.debt_old = customer_debt.summa
                            customer_debt.summa += i.baskets_total_price
                            i.debt_new = customer_debt.summa

                        i.save()
                        customer_debt.save()



    @property
    def debt_haqimiz(self):
        data = [
            {'summa': CustomerDebt.objects.filter(customer=self, valyuta=val, summa__gt=0).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all']}
            for val in Valyuta.objects.all()
        ]
        return data
    @property
    def debt_qarzimiz(self):
        data = [
            {'summa': CustomerDebt.objects.filter(customer=self, valyuta=val, summa__lt=0).aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all']}
            for val in Valyuta.objects.all()
        ]
        return data
    class Meta:
        verbose_name_plural = '7) Nasiyachilar'


class CustomerDebt(models.Model):
    customer = models.ForeignKey(Debtor, on_delete=models.CASCADE)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE)
    summa = models.IntegerField(default=0)
    start_summa = models.IntegerField(default=0)


#
# class DebtHistory(models.Model):
#     debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
#     product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
#     price = models.IntegerField(default=0)
#     debt_quan = models.IntegerField(default=0)
#     pay_quan = models.IntegerField(default=0)
#     debt = models.IntegerField(default=0)
#     pay = models.IntegerField(default=0)
#     difference = models.IntegerField(default=0)
#
#     class Meta:
#         verbose_name_plural = '8) Nasiya Tarixi'


class Debt(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    return_date = models.DateField()
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.debtor.fio

    @property
    def get_model(self):
        return self._meta.model_name

    class Meta:
        verbose_name_plural = 'Qarz Tarixi'


class PayHistory(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, blank=True, null=True)
    desktop_id = models.IntegerField(blank=True, null=True)
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE , blank=True, null=True)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, related_name='filial_pay', blank=True, null=True)
    som = models.IntegerField(default=0, null=True)
    dollar = models.IntegerField(default=0, null=True)
    click = models.IntegerField(default=0)
    plastik = models.IntegerField(default=0)
    currency = models.FloatField(default=0)
    comment = models.TextField(blank=True, null=True, default='Izoh yo`q')
    date = models.DateTimeField(default=timezone.now)

    summa = models.IntegerField(default=0, null=True)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    kassa = models.ForeignKey("KassaMerge", on_delete=models.CASCADE, null=True, blank=True)

    som_after = models.FloatField(default=0)
    dollar_after = models.FloatField(default=0)
    money_circulation = models.ForeignKey('MoneyCirculation', on_delete=models.CASCADE, null=True, blank=True)
    deliver_all_payment = models.ForeignKey(DeliverPaymentsAll, on_delete=models.CASCADE, null=True, blank=True)
    deliver_pay_History = models.ForeignKey(DeliverPayHistory, on_delete=models.CASCADE, null=True, blank=True)
    external_income_user = models.ForeignKey('ExternalIncomeUser', on_delete=models.CASCADE, null=True, blank=True)
    type_pay = models.IntegerField(choices=((1, 'Pay'),(2, 'Give')), default=1)
    summa = models.IntegerField(default=0)
    debt_old = models.IntegerField(default=0)
    debt_new = models.IntegerField(default=0)

    
    @property
    def model_name(self):
        return 'payhistory'
    
    @property
    def total_som(self):
        return self.som + self.click + self.plastik + self.dollar / (self.currency if self.currency else 1) 

    @property
    def get_model(self):
        return self._meta.model_name

    def save_kassa(self, kassa, old_values=None):
        """
        Kassa qiymatlarini yaratish va tahrirlashda yangilaydi.
        Agar eski qiymatlar bo'lsa, farq hisoblab, kassadagi qiymatlarni to'g'rilaydi.
        """
        if old_values:
            # Eski qiymatlarni olib tashlash
            kassa.som -= old_values['som']
            kassa.dollar -= old_values['dollar']
            kassa.plastik -= old_values['plastik']
            kassa.hisob_raqam -= old_values['click']

        # Yangi qiymatlarni qo'shish
        # kassa.som += self.som
        # kassa.dollar += self.dollar
        # kassa.plastik += self.plastik
        # kassa.hisob_raqam += self.click

        qancha_som = self.som
        qancha_dol = self.dollar
        plastik = self.plastik
        qancha_hisob_raqamdan = self.click


        kirim, created = Kirim.objects.get_or_create(payhistory=self)
        if qancha_som or (old_values and old_values['som']):
            kirim.qancha_som = qancha_som
            kassa.som += int(qancha_som)
            kirim.kassa_som_yangi = kassa.som
            kirim.kassa_som_eski = kirim.kassa_som_yangi - int(qancha_som)
            
        if plastik or (old_values and old_values['plastik']):
            kirim.plastik = plastik
            kassa.plastik += int(plastik)
            kirim.kassa_plastik_yangi = kassa.plastik
            kirim.kassa_plastik_eski = kirim.kassa_plastik_yangi - int(plastik)


        if qancha_dol or (old_values and old_values['dollar']):
            kirim.qancha_dol = qancha_dol
            kassa.dollar += int(qancha_dol)
            kirim.kassa_dol_yangi = kassa.dollar
            kirim.kassa_dol_eski = kirim.kassa_dol_yangi - int(qancha_dol)
        
        if qancha_hisob_raqamdan or (old_values and old_values['click']):
            kirim.qancha_hisob_raqamdan = qancha_hisob_raqamdan
            kassa.hisob_raqam += int(qancha_hisob_raqamdan)
            kirim.kassa_hisob_raqam_yangi = kassa.hisob_raqam
            kirim.kassa_hisob_raqam_eski = kirim.kassa_hisob_raqam_yangi - int(qancha_hisob_raqamdan)

        kirim.save()
        kassa.save()

        

    def save(self, *args, **kwargs):
        """
        PayHistory yaratilganda va tahrirlanganda kassa avtomatik yangilanadi.
        - Yaratishda: To'g'ridan-to'g'ri qo'shadi.
        - Tahrirda: Eski qiymatlarni olib tashlab, yangi qiymatlarni qo'shadi.
        """
        # Kassa aniqlash (masalan, filial orqali yoki boshqa usul bilan)
        # kassa = Kassa.objects.first()  # ⚠️ O'zingizga mos kassa tanlash mexanizmini qo'shing
        # old_values = None

        # if self.pk:
        #     # Tahrir holati uchun eski qiymatlarni olish
        #     old_instance = PayHistory.objects.get(pk=self.pk)
        #     old_values = {
        #         'som': old_instance.som,
        #         'dollar': old_instance.dollar,
        #         'plastik': old_instance.plastik,
        #         'click': old_instance.click,
        #     }

        super().save(*args, **kwargs)  # Avval model saqlanadi
        # if kassa and self.shop:
        #     self.save_kassa(kassa, old_values=old_values)

        
        

    class Meta:
        verbose_name_plural = '9) Tolov Tarixi'


class PayChecker(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
    agent = models.ForeignKey(MobilUser, on_delete=models.CASCADE, blank=True, null=True)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    click = models.FloatField(default=0)
    bank = models.FloatField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    currency = models.FloatField(default=0)
    comment = models.TextField(blank=True, null=True, default='Izoh yo`q')
    status = models.BooleanField(default=False)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.debtor.fio
    

class CartDebt(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    given_quan = models.FloatField(default=0)
    total = models.FloatField(default=0)
    return_quan = models.FloatField(default=0)
    return_sum = models.IntegerField(default=0)
    debt_quan = models.FloatField(default=0)
    debt_sum = models.FloatField(default=0)
    difference = models.FloatField(default=0)

    def __str__(self):
        return f'{self.debtor.fio} / {self.product.name}'

    class Meta:
        verbose_name_plural = 'CartDebt'


class ReturnProduct(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    return_quan = models.FloatField(default=0)
    som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)
    difference = models.FloatField(default=0)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.PositiveIntegerField(default=0) 
    barcode = models.CharField(max_length=255)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def get_model(self):
        return self._meta.model_name

    def __str__(self):
        return self.product.name
    

    class Meta:
        verbose_name_plural = 'Return Product'


class Pereotsenka(models.Model):
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = 'Pereotsenka'


class ChangePrice(models.Model):
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = 'ChangePrice'


class ChangePriceItem(models.Model):
    changeprice = models.ForeignKey(ChangePrice, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    old_som = models.IntegerField(default=0)
    old_dollar = models.IntegerField(default=0)
    new_som = models.IntegerField(default=0)
    new_dollar = models.IntegerField(default=0)
    quantity = models.FloatField(default=0)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name_plural = 'ChangePriceIten'


class ReturnProductToDeliver(models.Model):
    deliver = models.ForeignKey(Deliver, on_delete=models.CASCADE)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)
    kurs = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    is_activate = models.BooleanField(default=True)

    def __str__(self):
        return self.deliver.name

    class Meta:
        verbose_name_plural = 'Return Product To Deliver'


class ReturnProductToDeliverItem(models.Model):
    returnproduct = models.ForeignKey(ReturnProductToDeliver, on_delete=models.CASCADE, related_name='returnproducttodeliver')
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)
    quantity = models.FloatField(default=0)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def total_som(self):
        return float(self.som * self.quantity)
    
    @property
    def total_dollar(self):
        return float(self.dollar * self.quantity)

    def __str__(self):
        return str(self.returnproduct.id)

    class Meta:
        verbose_name_plural = 'Return Product To Deliver Item'
    

@receiver(post_save, sender=ReturnProductToDeliverItem)
def return_product_history(sender, instance, **kwargs):
    payments = DeliverPayments.objects.filter(deliver=instance.returnproduct.deliver).order_by('id')
    if payments.exists():
        payment = payments.first()
    else:
        payment = DeliverPayments.objects.create(deliver=instance.returnproduct.deliver)
        
    payment.deliver = instance.returnproduct.deliver
    deliver = instance.returnproduct.deliver

    payment1 = DeliverPaymentsAll.objects.create()
    payment1.return_total += float(instance.total_som) if instance.total_som else 0
    payment1.return_total += (float(instance.total_dollar) if instance.total_dollar else 0) * Course.objects.last().som
    
    
    deliver.som += payment1.return_total
    payment1.left = deliver.som
    
    payment.payments.add(payment1)
    deliver.save()
    payment1.save()
    payment.save()


class Kamomad(models.Model):
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    valyuta = models.CharField(max_length=25)
    difference_sum = models.IntegerField(default=0)
    difference_dollar = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now=True)


class Exchange(models.Model):
    kurs = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now=True)


class Kassa(models.Model):
    nomi = models.CharField(max_length=50)
    som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)
    plastik = models.IntegerField(default=0)
    hisob_raqam = models.IntegerField(default=0)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, null=True, blank=True)
    is_main = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.nomi

class KassaNew(models.Model):
    name = models.CharField(max_length=100)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_main = models.BooleanField(default=False)
    kassa_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

class KassaMerge(models.Model):
    kassa = models.ForeignKey(KassaNew, on_delete=models.CASCADE, null=True, blank=True)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE)
    start_summa = models.IntegerField(default=0)
    summa = models.IntegerField(default=0)
    start_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

class ChiqimTuri(models.Model):
    nomi = models.CharField(max_length=50)
    kunlik = models.BooleanField(default=False, verbose_name='kozda tutilgan harajat')
    for_employee = models.BooleanField(default=False)
    for_product = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return self.nomi



class ChiqimCategory(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class ChiqimSubCategory(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ChiqimCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class Chiqim(models.Model):
    qayerga = models.ForeignKey(ChiqimTuri, on_delete=models.PROTECT, null=True, blank=True)

    subcategory = models.ForeignKey(ChiqimSubCategory, on_delete=models.PROTECT, null=True, blank=True)

    
    kassa_som_eski = models.IntegerField(default=0)
    qancha_som  = models.IntegerField(default=0)
    qancha_som_eski  = models.IntegerField(default=0)
    kassa_som_yangi = models.IntegerField(default=0)
    
    kassa_dol_eski = models.IntegerField(default=0)
    qancha_dol = models.IntegerField(default=0)
    qancha_dol_eski = models.IntegerField(default=0)
    kassa_dol_yangi = models.IntegerField(default=0)
    
    kassa_plastik_eski = models.IntegerField(default=0)
    plastik = models.IntegerField(default=0)
    plastik_eski = models.IntegerField(default=0)
    kassa_plastik_yangi = models.IntegerField(default=0)
    
    kassa_hisob_raqam_eski = models.IntegerField(default=0)
    qancha_hisob_raqamdan = models.IntegerField(default=0)
    qancha_hisob_raqamdan_eski = models.IntegerField(default=0)
    kassa_hisob_raqam_yangi = models.IntegerField(default=0)
    deliver = models.ForeignKey(Deliver, on_delete=models.PROTECT, null=True, blank=True)
    
    izox = models.TextField()
    qachon  = models.DateTimeField(auto_now_add=True)

    summa = models.IntegerField(default=0, null=True)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    kassa = models.ForeignKey("KassaMerge", on_delete=models.CASCADE, null=True, blank=True)
    kassa_new = models.FloatField(default=0)
    currency = models.IntegerField(default=0)
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True)
    mobil_user = models.ForeignKey(MobilUser, on_delete=models.SET_NULL, blank=True, null=True)
    deliver = models.ForeignKey(Deliver, on_delete=models.CASCADE, blank=True, null=True)
    deliverpayment = models.ForeignKey(DeliverPaymentsAll, on_delete=models.CASCADE, blank=True, null=True)
    is_approved = models.BooleanField(default=True) 

    def __str__(self) -> str:
        return f'{self.qayerga.nomi if self.qayerga else ""} {str(self.qachon)}'
    
    @property
    def som(self):
        currency = Course.objects.last().som
        return self.qancha_som + self.plastik + self.qancha_hisob_raqamdan + self.qancha_dol * currency

    @property
    def summa_for_valutas(self):
        valutas = Valyuta.objects.all()
        return [{
            "summa": self.summa if self.valyuta == v else 0 
        } for v in valutas]





class DesktopChiqim(models.Model):
    qayerga = models.ForeignKey(ChiqimTuri, on_delete=models.PROTECT, null=True, blank=True)
    
    qancha_som  = models.IntegerField(default=0)
    qancha_dol = models.IntegerField(default=0)
    plastik = models.IntegerField(default=0)
    qancha_hisob_raqamdan = models.IntegerField(default=0)

    
    izox = models.TextField(blank=True, null=True)
    qachon  = models.DateTimeField(auto_now_add=True)

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    
class Kirim(models.Model):
    qayerga = models.ForeignKey(ChiqimTuri, on_delete=models.CASCADE, null=True, blank=True)
    payhistory = models.ForeignKey(PayHistory, on_delete=models.CASCADE, null=True, blank=True)
    
    kassa_som_eski = models.IntegerField(default=0)
    qancha_som  = models.IntegerField(default=0)
    qancha_som_eski  = models.IntegerField(default=0)
    kassa_som_yangi = models.IntegerField(default=0)
    
    kassa_dol_eski = models.IntegerField(default=0)
    qancha_dol = models.IntegerField(default=0)
    qancha_dol_eski = models.IntegerField(default=0)
    kassa_dol_yangi = models.IntegerField(default=0)
    
    kassa_hisob_raqam_eski = models.IntegerField(default=0)
    qancha_hisob_raqamdan = models.IntegerField(default=0)
    qancha_hisob_raqamdan_eski = models.IntegerField(default=0)
    kassa_hisob_raqam_yangi = models.IntegerField(default=0)
    
    kassa_plastik_eski = models.IntegerField(default=0)
    plastik = models.IntegerField(default=0)
    plastik_eski = models.IntegerField(default=0)
    kassa_plastik_yangi = models.IntegerField(default=0)

    summa = models.IntegerField(default=0, null=True)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    kassa = models.ForeignKey("KassaMerge", on_delete=models.CASCADE, null=True, blank=True)
    kassa_new = models.FloatField(default=0)
    
    currency = models.IntegerField(default=0, null=True)
    izox = models.TextField()
    qachon  = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    @property
    def summa_for_valutas(self):
        valutas = Valyuta.objects.all()
        return [{
            "summa": self.summa if self.valyuta == v else 0 
        } for v in valutas]

    def __str__(self) -> str:
        return f'{str(self.qachon)}'

    def save(self, *args, **kwargs):
        if self.plastik and self.kassa_hisob_raqam_yangi != 0 and self.kassa_hisob_raqam_eski != 0:
            self.kassa_plastik_eski = self.kassa_hisob_raqam_eski
            self.kassa_plastik_yangi = self.kassa_hisob_raqam_yangi
        

        if self.qancha_hisob_raqamdan and self.kassa_plastik_eski != 0 and self.kassa_plastik_yangi != 0:
            self.kassa_hisob_raqam_eski = self.kassa_plastik_eski
            self.kassa_hisob_raqam_yangi = self.kassa_plastik_yangi

        if self.payhistory and not self.payhistory.shop:
            self.payhistory.som = self.qancha_som
            self.payhistory.dollar = self.qancha_dol
            self.payhistory.plastik = self.plastik
            self.payhistory.click = self.qancha_hisob_raqamdan
            self.payhistory.save(update_fields=['som', 'dollar', 'plastik', 'click'])

        super().save(*args, **kwargs)


import binascii
import os
from django.utils.translation import gettext_lazy as _


class MyOwnToken(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField(_("Key"), max_length=40, primary_key=True)

    user = models.OneToOneField(
        MobilUser, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name="Company"
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Mobile Token")
        verbose_name_plural = _("Mobile Tokens")


    def save(self, *args, **kwargs):
        if not self.key:
            self.key = generate_key()
        return super(MyOwnToken, self).save(*args, **kwargs)

    def __str__(self):
        return self.key

def generate_key():
    return binascii.hexlify(os.urandom(20)).decode()


class MCart(models.Model):
    user = models.ForeignKey(MobilUser, on_delete=models.CASCADE)
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()
    status = models.CharField(choices=(
        ('1', 'Maxsulot Savatchada'),
        ('2', 'Sotib olingan')
    ), max_length=255, default=1)
    total = models.IntegerField(blank=True, null=True)
    applied = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)
    
    @property
    def get_date(self):
        morder = self.morders.last()
        if morder:
            return morder.date
        return None
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        employes = MobilUser.objects.all()
        for i in employes:
            obj, created = MobilPayment.objects.get_or_create(m_user=i, sana=self.get_date)
            obj.total_price = MCart.objects.filter(morders__sold=True, morders__date__date=self.get_date).distinct().aggregate(all=Coalesce(Sum('quantity'), 0))['all']
            obj.save()        
           
    
    
    class Meta:
        verbose_name_plural = 'Mobile Cart'

class Telegramid(models.Model):
    name = models.CharField(max_length=255)
    telegram_id = models.IntegerField()

class Banner(models.Model):
    image = models.ImageField(upload_to="banner/")

    class Meta:
        verbose_name_plural = "Mobile Banner"

class MOrder(models.Model):
    user = models.ForeignKey(MobilUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(MCart, related_name='morders')
    date = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE, null=True, blank=True)
    sold = models.BooleanField(default=False)

    
    class Meta:
        verbose_name_plural = "Mobile order"

import requests

# @receiver(sender=MOrder, signal=[pre_save])
# def send_order(sender, instance, *args, **kwargs):
#     # if created:
#         products = ""
#         total = 0
#         for i in instance.products.all():
#             cart = MCart.objects.get(id=i.id)
#             dt = f"- {cart.product.name} -> {cart.quantity}ta * {cart.price}\n\n"
#             products += dt
#             total += cart.price * cart.quantity
#         text = 'Buyurtma: '+ str(instance.id) + '\nMijoz: ' + instance.user.username + '\Mijoz telefon raqami: ' + str(instance.user.phone) + '\n\nMaxsulotlar: \n\n' + products + '\njami: ' + str(total)
#         url = 'https://api.telegram.org/bot6007881568:AAHIQFBkTNLwsbE0C5rmt67IH16F6BRjKWQ/sendMessage?chat_id=-1001695536220'

#         requests.get(url + '&text=' + text)




class CashboxReceive(models.Model):
    CURRENCY = (
        ("so'm", "so'm"),
        ("dollar", "dollar"),
        ('carta', 'carta'),
        ('utkazma', 'utkazma')
    )
    STATUS = (
        ("waiting", "waiting"),
        ("accepted", "accepted"),
        ("rejected", "rejected")
    )
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    kassa_sum_old = models.FloatField()
    total_sum = models.FloatField()
    kassa_sum_new = models.FloatField()
    total_dollar = models.FloatField(blank=True, null=True)
    currency = models.CharField(max_length=20, choices=CURRENCY, default="so'm")
    date = models.DateField()
    status = models.CharField(max_length=255, choices=STATUS, default="waiting")
    description = models.TextField(blank=True)
    director_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class FilialExpense(models.Model):
    CURRENCY = (
        ("so'm", "so'm"),
        ("dollar", "dollar"),
        ('carta', 'carta'),
        ('utkazma', 'utkazma')
    )
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    category = models.ForeignKey('FilialExpenseCategory', on_delete=models.CASCADE)
    subcategory = models.CharField(max_length=255)
    kassa_sum_old = models.FloatField()
    total_sum = models.FloatField()
    kassa_sum_new = models.FloatField()
    
    currency = models.CharField(max_length=20, choices=CURRENCY, default="so'm")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Filial chiqim"
        verbose_name_plural = "Filial chiqimlar"

    def __str__(self) -> str:
        return self.filial.name
    
    
class FilialExpenseCategory(models.Model):
    title = models.CharField(max_length=255, unique=True)
    kunlik = models.BooleanField(default=False, verbose_name='kozda tutilgan harajat')

    class Meta:
        verbose_name = "Filial chiqim turi"
        verbose_name_plural = "Filial chiqim turlari"

    def __str__(self) -> str:
        return self.title




class SekretKey(models.Model):
    key = models.CharField(max_length=200)

    def __str__(self):
        return self.key


# shop api

class Region(models.Model):
    name = models.CharField(max_length=40)
    number = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Viloyatlar'
        
    

class Teritory(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    number = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Hududlar'


class PriceType(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=150)
    is_activate = models.BooleanField(default=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Narx turi'
        ordering = ['id']

class ProductPriceType(models.Model):
    type = models.ForeignKey(PriceType, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE, related_name='price_types')
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    price_dollar = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = 'Maxsulot narx turi'


class OneDayPice(models.Model):
    one_day_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    bet = models.FloatField(default=1)
    is_status = models.BooleanField(default=True)
    sana = models.DateField(null=True)
    
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        

class FlexPrice(models.Model):
    user_profile = models.ForeignKey(UserProfile,  on_delete=models.CASCADE)
    is_status = models.BooleanField(default=True)
    flex_price =  models.DecimalField(max_digits=20, decimal_places=2,default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    sana = models.DateField(null=True)
    summa_fex = models.DecimalField(max_digits=20, decimal_places=2, default=0)


    # @property
    # def cart_count(self):
    #     total = Cart.objects.select_related('shop', 'shop__saler').filter(shop__saler__staff=3, shop__date__date=self.sana).distinct().aggregate(all=Coalesce(Sum('quantity'), 0))['all']

    #     return total
    
class MobilPayment(models.Model):
    m_user = models.ForeignKey(MobilUser , on_delete=models.CASCADE)
    sana  = models.DateField(default=timezone.now, null=True)
    total_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    flex_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    is_status = models.BooleanField(default=True)
    
class DesktopKassa(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    kassa_name = models.CharField(max_length=255)
    operation_name = models.CharField(max_length=255)
    debtor = models.CharField(blank=True, null=True,max_length=255)
    qoldik = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    summa = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    yangi_qoldik = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    desktop_id = models.IntegerField(unique=True)


class AllDaySumEmployee(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    date = models.DateField()
    fix = models.FloatField(default=0)
    flex = models.FloatField(default=0)
    pay = models.FloatField(default=0,verbose_name='Tolandi')
    rest = models.FloatField(default=0,verbose_name='Qoldik')
    summa = models.FloatField(default=0)
    quantity = models.FloatField(default=0)
    flex_price = models.FloatField(default=0)
    izox = models.CharField(max_length=255)
    is_status = models.BooleanField(default=True)

    @property
    def ishladi(self):
        return self.flex_price * self.quantity





class ProductFilialDaily(models.Model):
    rest = models.FloatField(default=0)
    obyekt = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)


class DebtorDaily(models.Model):
    rest = models.FloatField(default=0)
    obyekt = models.ForeignKey(Debtor, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)


class DeliverDaily(models.Model):
    rest = models.FloatField(default=0)
    obyekt = models.ForeignKey(Deliver, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)


class KassaDaily(models.Model):
    som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)
    plastik = models.IntegerField(default=0)
    hisob_raqam = models.IntegerField(default=0)

    obyekt = models.ForeignKey(Kassa, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)


class MoneyCirculation(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    manba = models.CharField(max_length=255, null=True, blank=True)
    sub_manba = models.CharField(max_length=255, null=True, blank=True)

    # xarajat_turi = models.ForeignKey()
    chiqim_turi = models.ForeignKey(ChiqimTuri, on_delete=models.CASCADE, null=True, blank=True)

    manba_turi = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)


class WriteOff(models.Model):
    number = models.IntegerField(default=0)
    date_time = models.DateTimeField(auto_now_add=True)
    kurs = models.FloatField(default=0)
    money_type = models.ForeignKey(MoneyCirculation, on_delete=models.CASCADE, null=True, blank=True)
    product_filial = models.ForeignKey(Filial, on_delete=models.CASCADE, null=True, blank=True)
    izoh = models.TextField(default="")
    is_activate = models.BooleanField(default=True)

    @property
    def summa_product_som(self):
        return sum(i.summa_total_som for i in  WriteOffItem.objects.filter(write_off=self))
    
    @property
    def summa_product_dollar(self):
        return sum(i.summa_total_dollar for i in  WriteOffItem.objects.filter(write_off=self))
    @property
    def summa_quantity(self):
        return sum(i.quantity for i in  WriteOffItem.objects.filter(write_off=self))

class WriteOffItem(models.Model):
    write_off = models.ForeignKey(WriteOff, on_delete=models.CASCADE, related_name='writeoffitem')
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)

    @property
    def summa_total_dollar(self):
        if self.product:
            if self.product.dollar > 0:
                return self.product.som * self.quantity
        return 0
    
    @property
    def summa_total_som(self):
        if self.product:
            if self.product.som > 0:
                return self.product.som * self.quantity
        return 0



class RejaTushum(models.Model):
    date = models.DateField(auto_now_add=True)
    payment_date = models.DateField(null=True, blank=True)
    total = models.IntegerField(default=0)
    plan_total = models.IntegerField(default=0)
    kurs = models.IntegerField(default=0)
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE, null=True, blank=True)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True , blank=True)
    from_shop = models.BooleanField(default=False)

class RejaChiqim(models.Model):
    date = models.DateField(auto_now_add=True)
    payment_date = models.DateField(null=True, blank=True)
    total = models.IntegerField(default=0)
    plan_total = models.IntegerField(default=0)
    kurs = models.IntegerField(default=0)
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE, null=True, blank=True)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True , blank=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True , blank=True)
    from_shop = models.BooleanField(default=False)
    
# class ProductFilialDaily(models.Model):
#     rest = models.FloatField(default=0)
#     obyekt = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
#     date = models.DateField(defaul=timezone.now().date)



# class ProductFilialDaily(models.Model):
#     rest = models.FloatField(default=0)
#     object = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
#     date = models.DateField(defaul=timezone.now().date)



# class ProductFilialDaily(models.Model):
#     rest = models.FloatField(default=0)
#     object = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
#     date = models.DateField(defaul=timezone.now().date)


class ExternalIncomeUserTypes(models.Model):
    name = models.CharField(max_length=200)
    tartib_raqam = models.PositiveIntegerField(unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)



class ExternalIncomeUser(models.Model):
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    type = models.ForeignKey(ExternalIncomeUserTypes, on_delete=models.PROTECT)
    tartib_raqam = models.PositiveIntegerField(unique=True)
    date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save()
        for val in Valyuta.objects.all():
            ExternalIncomeUserDebt.objects.get_or_create(income=self, valyuta=val)

    @property
    def summa_pay(self):
        pay = ExternalIncomeUserPayment.objects.filter(external_income_user=self,type_pay=1)
        data = {
            'summa':pay.aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all'],
        }
        return data
    @property
    def summa_give(self):
        pay = ExternalIncomeUserPayment.objects.filter(external_income_user=self,type_pay=2)
        data = {
            'summa':pay.aggregate(all=Coalesce(Sum('summa'), 0 , output_field=IntegerField()))['all'],
        }
        return data

    def income_refresh_debt(self):
        pay_history = PayHistory.objects.filter(external_income_user=self).order_by('-id')
        customer_debts = ExternalIncomeUserDebt.objects.filter(income=self)

        for valyuta in Valyuta.objects.all():
            customer_debt = customer_debts.filter(valyuta=valyuta).last()
            if customer_debt:
                customer_debt.summa = customer_debt.start_summa
                customer_debt.save()

                for i in pay_history:
                    if i.valyuta == valyuta:
                        i.debt_old = customer_debt.summa
                        if i.type_pay == 1:
                            customer_debt.summa += i.summa
                        else:
                            customer_debt.summa -= i.summa
                        i.debt_new = customer_debt.summa
                    i.save()
                    customer_debt.save()


class ExternalIncomeUserDebt(models.Model):
    income = models.ForeignKey(ExternalIncomeUser, on_delete=models.CASCADE)
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE)
    summa = models.IntegerField(default=0)
    start_summa = models.IntegerField(default=0)

class ExternalIncomeUserPayment(models.Model):
    external_income_user = models.ForeignKey(ExternalIncomeUser, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    summa = models.IntegerField(default=0)
    type_pay = models.IntegerField(choices=((1, 'Pay'),(2, 'Give')), default=1)
    comment = models.TextField(blank=True, null=True, default='Izoh yo`q')
    valyuta = models.ForeignKey(Valyuta, on_delete=models.CASCADE, null=True, blank=True)

class MainToolType(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

from dateutil.relativedelta import relativedelta


class MainTool(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    inventory_number = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    tool_type = models.ForeignKey(MainToolType, on_delete=models.CASCADE)
    summa = models.FloatField(default=0)
    wear = models.FloatField(default=0, verbose_name='Toplangan eskirish')
    today_stayed = models.FloatField(default=0, verbose_name='Bugungi qoldiq')
    use_month = models.IntegerField(default=0, verbose_name='Foydalanish oyi')
    wear_month_summa = models.IntegerField(default=0, verbose_name='Oylik eskirish summasi')
    is_active = models.BooleanField(default=True)
    date = models.DateField(default=timezone.now)

    @property
    def sum_wear_month_summa(self):
        today = timezone.now().date()

        if self.date > today:
            return 0

        date_diff = relativedelta(today, self.date)
        
        total_months = date_diff.years * 12 + date_diff.months
        
        if total_months >= self.use_month:
            return self.summa
        
        return self.wear_month_summa * total_months

    @property
    def sum_today_stayed(self):
        if self.sum_wear_month_summa > 0:
            return self.summa - self.sum_wear_month_summa
        return 0 

    class Meta:
        verbose_name_plural = 'Asossiy Vosita'