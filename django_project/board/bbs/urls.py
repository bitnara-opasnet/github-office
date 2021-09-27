from django.contrib import admin
from django.urls import path
# from . import views
from .views import *

# urlpatterns = [
#     path('', views.index, name='index'),
#     path('list/', views.list, name='list'),
# ] 

urlpatterns=[
    path('', index, name='index'),
    path('list/', list, name='list'),
    path('list/<int:pk>', detail, name="detail"),
    path('input', input, name="input"),
    path('list/<int:pk>/delete', delete, name="delete"),
]