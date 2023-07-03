from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
   path('api-token-auth/', obtain_auth_token),
   path('categories/', views.CategoryView.as_view()),
   path('menu-items/', views.MenuItemsView.as_view()),
   path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
   path('groups/manager/users/', views.ManagerView.as_view()),
   path('groups/manager/users/<int:pk>', views.ManagerDeleteView.as_view()),
   path('groups/delivery-crew/users/', views.DeliveryView.as_view()),
   path('groups/delivery-crew/users/<int:pk>', views.DeliveryDeleteView.as_view()),
   path('cart/menu-items/', views.CartMenuItemView.as_view()),  
   path('orders/', views.OrdersView.as_view()),
   path('orders/<int:pk>', views.SingleOrderView.as_view()),
]

