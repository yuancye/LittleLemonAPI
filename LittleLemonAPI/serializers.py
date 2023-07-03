from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User, Group

class UserSerializer(serializers.ModelSerializer):
   class Meta():
      model = User
      fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta():
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'featured', 'price', 'category', 'category_id']


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # Assign the user to the Manager group
        manager_group = Group.objects.get(name='Manager')
        user.groups.add(manager_group)
        return user

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        delivery_group = Group.objects.get(name='Delivery Crew')
        user.groups.add(delivery_group)
        return user

class CartSerializer(serializers.ModelSerializer):
    username_id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    menuitem_name = serializers.ReadOnlyField(source='menuitem.title')
    price = serializers.SerializerMethodField(read_only=True)
    unit_price = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Cart
        fields = ['username_id', 'username', 'menuitem', 'menuitem_name', 'unit_price', 'quantity', 'price']
    
    def get_price(self, obj):
        return obj.quantity * obj.unit_price

    def get_unit_price(self, obj):
        return obj.menuitem.price
    
    def create(self, validated_data):
        menuitem = validated_data['menuitem']
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = menuitem.price * validated_data['quantity']
        return super().create(validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['username']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta():
        model = Order
        fields = ['id','user','total','status','delivery_crew','date']


class SingleHelperSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = ['title','price']

class SingleOrderSerializer(serializers.ModelSerializer):
    menuitem = SingleHelperSerializer()
    class Meta():
        model = OrderItem
        fields = ['menuitem','quantity']

class OrderPutSerializer(serializers.ModelSerializer):
    class Meta():
        model = Order
        fields = ['delivery_crew']

