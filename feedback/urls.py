from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_feedback, name='submit_feedback'),
    path('view/', views.view_feedback, name='view_feedback'),
    path('add-service/', views.add_service, name='add_service'),
]