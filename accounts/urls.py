from django.urls import path
from . import views

urlpatterns = [
    path('generate-admin-key/', views.generate_admin_key, name='generate_admin_key'),
    path('generate-customer-key/', views.generate_customer_key, name='generate_customer_key'),
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
    path('set-status/', views.set_status, name='set_status'),
    path('delete-user/', views.delete_user, name='delete_user'),
    path('view-customers/', views.view_customers, name='view_customers'),
    path('view-admins/', views.view_admins, name='view_admins'),  
]#add view admins and view customers
