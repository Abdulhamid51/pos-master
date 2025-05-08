from rest_framework import serializers
from .models import *
from rest_framework.authtoken.models import Token


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'


class DebtorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debtor
        fields = '__all__'

class DesktopKassaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesktopKassa
        fields = '__all__'

class MobilUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = MobilUser
        fields = ['id', 'phone', 'username']

class PayHistorySerializer(serializers.ModelSerializer):
    debtor = DebtorSerializer(many=False)

    class Meta:
        model = PayHistory
        fields = "__all__"

class PayCheckerSerializer(serializers.ModelSerializer):
    agent = MobilUserSerializer(many=False)
    debtor = DebtorSerializer(many=False)

    class Meta:
        model = PayChecker
        fields = "__all__"

class MCartSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['name'] = instance.product.name
        data['product'] = ProductFilialSerializer(instance.product).data
        return data
    class Meta:
        model = MCart
        fields = "__all__"

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class MOrderSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        debtor = {
            "id": 0,
            "image": None,
            "fio": None,
            "phone1": None,
            "phone2": None,
            "som": 0,
            "dollar": 0,
            "difference": 0,
            "lan": 0,
            "lat": 0,
            "debt_return": None,
            "date": None,
            "inn": None,
            "company": None,
            "type": None,
            "teritory": None,
            "agent": 0
        }
        data['products'] = MCartSerializer(instance.products, many=True).data
        data['debtor'] = DebtorSerializer(instance.debtor, many=False).data if instance.debtor else debtor
        data['user'] = MobilUserSerializer(instance.user, many=False).data if instance.user else {'id': 0}
        return data
    class Meta:
        model = MOrder
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'staff', 'filial']


class FilialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filial
        fields = '__all__'


class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = '__all__'


class DeliverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deliver
        fields = '__all__'


class ProductFilialSerializer(serializers.ModelSerializer):
    def to_representation(self, instance: ProductFilial):
        data = super().to_representation(instance)
        data['filial'] = FilialSerializer(instance.filial, many=False).data
        return data
    # filial = FilialSerializer(read_only = True)
    class Meta:
        model = ProductFilial
        fields = '__all__'
        
# data = []
# for i in ProductFilial.objects.all():
#     data.append({
#         'id': i.id,
#         'barcode': i.barcode
#     })

# print(data)

class ProductFilialSerializer2(serializers.ModelSerializer):
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['filial'] = FilialSerializer(instance.filial, many=False).data
    #     return data
    # filial = FilialSerializer(read_only = True)
    class Meta:
        model = ProductFilial
        fields = '__all__'


class ProductFilialSerializerWithCourse(serializers.ModelSerializer):

    class Meta:
        model = ProductFilial
        fields = '__all__'


class RecieveSerializer(serializers.ModelSerializer):
    filial = FilialSerializer(many=False, read_only=True)

    class Meta:
        model = Recieve
        fields = ["id", "filial", "name", "date", "som", "sum_sotish_som", "dollar", "sum_sotish_dollar", "status", "deliver"]


class RecieveItemSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['prices'] = ProductPriceTypeSerializer(ProductPriceType.objects.filter(product=instance.product), many=True).data
        return data
    
    product = ProductFilialSerializer(read_only=True, many=False)

    class Meta:
        model = RecieveItem
        fields = ["id", "recieve", "product", "som", "sotish_som", "dollar", "sotish_dollar", "kurs", "quantity"]


class FakturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faktura
        fields = '__all__'


class FakturaItemSerializer(serializers.ModelSerializer):
    product = ProductFilialSerializer(read_only=True)

    class Meta:
        model = FakturaItem
        fields = '__all__'


class FakturaItemReadSerializer(serializers.ModelSerializer):
    product = ProductFilialSerializer(read_only=True)

    class Meta:
        model = FakturaItem
        fields = '__all__'


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


# class DebtHistorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DebtHistory
#         fields = '__all__'


class DebtSerializer(serializers.ModelSerializer):
    debtor = DebtorSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)

    class Meta:
        model = Debt
        fields = '__all__'


class PayHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PayHistory
        fields = '__all__'


class CartDebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartDebt
        fields = '__all__'


class ReturnProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProduct
        fields = '__all__'


class ChangePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangePrice
        fields = '__all__'


class ChangePriceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangePriceItem
        fields = '__all__'


class ReturnProductToDeliverSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProductToDeliver
        fields = '__all__'


class ReturnProductToDeliverItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProductToDeliverItem
        fields = '__all__'


class KamomadModalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kamomad
        fields = '__all__'

        
        
        
        
class FilialExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FilialExpenseCategory
        fields = '__all__'
        
        
        
class FilialExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilialExpense
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['filial'] = instance.filial.name
        data['category'] = instance.category.title
        return data
    
class CashboxReceiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashboxReceive
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['filial'] = instance.filial.name
        return data


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class PriceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceType
        fields = '__all__'


class ChiqimTuriSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChiqimTuri
        fields = '__all__'


class ProductPriceTypeSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['product'] = ProductFilialSerializer(instance.product, many=False).data
        data['type_data'] = PriceTypeSerializer(instance.type, many=False).data
        data['name'] = instance.type.name if instance.type else None
        data['type'] = instance.type.code if instance.type else None
        return data
    class Meta:
        model = ProductPriceType
        fields = '__all__'



class DesktopChiqimSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['qayerga'] = ChiqimTuriSerializer(instance.qayerga, many=False).data
        data['user_profile'] = {
            "id": instance.user_profile.id,
            "first_name": instance.user_profile.first_name,
            "last_name": instance.user_profile.last_name,
        } if instance.user_profile else None
        return data
    class Meta:
        model = DesktopChiqim
        fields = '__all__'

# pro = ProductFilial.objects.all()
# for i in pro:
#     print(i.barcode)


class ProductFilialLISTSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFilial
        fields = ['barcode', 'quantity']