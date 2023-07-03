from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from rest_framework import generics, status, viewsets, filters
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.response import Response


from datetime import datetime, date
from decimal import Decimal
import math
from .models import *
from .serializers import *
from .permissions import *
from .paginations import *


#api/catrgory
class CategoryView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]

# api/menu-items
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemsSerializer  
    ordering_fields=['price']
    filterset_fields = ['price', 'featured']
    search_fields = ['title']  
    pagination_class = MenuItemPagination
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

# api/menu-items/pk
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all() 
    serializer_class = MenuItemsSerializer
   
    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]


# /api/groups/manager/users
class ManagerView(generics.ListCreateAPIView):
    queryset = Group.objects.get(name='Manager').user_set.all()
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
#    def get_permissions(self):
#       return [IsAdminUser()]

# /api/groups/manager/users/pk
class ManagerDeleteView(generics.RetrieveDestroyAPIView):
    queryset = Group.objects.get(name='Manager').user_set.all()
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

# /api/groups/delivery-crew/users/
class DeliveryView(generics.ListCreateAPIView):
    queryset = Group.objects.get(name='Delivery Crew').user_set.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

# /api/groups/delivery-crew/users/pk
class DeliveryDeleteView(generics.RetrieveDestroyAPIView):
    queryset = Group.objects.get(name='Delivery Crew').user_set.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

# /api/cart/menu-items/
class CartMenuItemView(generics.ListCreateAPIView):
    # queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        return Cart.objects.all().filter(user = self.request.user)

    def perform_create(self, serializer):     
        serializer.save(user=self.request.user)
        
    def delete(self, request, *args, **kwargs):
        # cart = Cart.objects.all()
        # cart.delete()
        Cart.objects.filter(user=request.user).delete()
        self.destroy(request, *args, **kwargs)
        return Response({'message': 'all items deleted'}, status.HTTP_200_OK)


# api/orders
class OrdersView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderSerializer
    ordering_fields = ['total', 'date']
    filterset_fields = ['total', 'date', 'status']
    search_fields = ['status']
    
    def get_queryset(self, *args, **kwargs):
        if self.request.user.groups.filter(name='Managers').exists() or self.request.user.is_superuser == True :
            query = Order.objects.all()
        elif self.request.user.groups.filter(name='Delivery Crew').exists():
            query = Order.objects.filter(delivery_crew=self.request.user)
        else:
            query = Order.objects.filter(user=self.request.user)
        return query

    def get_permissions(self):       
        if self.request.method == 'GET' or 'POST' : 
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        return[permission() for permission in permission_classes]

    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user)
        x=cart.values_list()
        if len(x) == 0:
            return HttpResponseBadRequest()
        total = math.fsum([float(x[-1]) for x in x])
        order = Order.objects.create(user=request.user, status=False, total=total, date=date.today())
        for i in cart.values():
            menuitem = get_object_or_404(MenuItem, id=i['menuitem_id'])
            orderitem = OrderItem.objects.create(order=order, menuitem=menuitem, quantity=i['quantity'])
            orderitem.save()
        cart.delete()
        return JsonResponse(status=201, data={'message':'Your order has been placed! Your order number is {}'.format(str(order.id))})

# api/orders/pk
class SingleOrderView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = SingleOrderSerializer
    
    def get_permissions(self):
        order = Order.objects.get(pk=self.kwargs['pk'])
        if self.request.user == order.user and self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        elif self.request.method == 'PUT' or self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsDeliveryCrew | IsManager | IsAdminUser]
        return[permission() for permission in permission_classes] 

    def get_queryset(self, *args, **kwargs):
            query = OrderItem.objects.filter(order_id=self.kwargs['pk'])
            return query


    def patch(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order.status = not order.status
        order.save()
        return JsonResponse(status=200, data={'message':'Status of order #'+ str(order.id)+' changed to '+str(order.status)})

    def put(self, request, *args, **kwargs):
        serialized_item = OrderPutSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        order_pk = self.kwargs['pk']
        crew_pk = request.data['delivery_crew'] 
        order = get_object_or_404(Order, pk=order_pk)
        crew = get_object_or_404(User, pk=crew_pk)
        order.delivery_crew = crew
        order.save()
        return JsonResponse(status=201, data={'message':str(crew.username)+' was assigned to order #'+str(order.id)})

    def delete(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order_number = str(order.id)
        order.delete()
        return JsonResponse(status=200, data={'message':'Order #{} was deleted'.format(order_number)})


