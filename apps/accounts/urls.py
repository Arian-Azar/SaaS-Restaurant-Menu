from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.RestaurantRegisterView.as_view(), name='register'),
    path('login/', views.RestaurantOwnerLoginView.as_view(), name='login'),
    path('logout/', views.RestaurantOwnerLogoutView.as_view(), name='logout'),
]
