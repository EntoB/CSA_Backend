from django.urls import path
from . import views

urlpatterns = [
    path('generate-admin-key/', views.generate_admin_key, name='generate_admin_key'),
    path('generate-customer-key/', views.generate_customer_key, name='generate_customer_key'),
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
]
