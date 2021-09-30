from django.contrib import admin
from django.urls import path
from . import views
from .views import *

# urlpatterns = [
#     path('', views.index, name='index'),
#     path('list/', views.list, name='list'),
# ] 

urlpatterns=[
    path('', index, name='index'),
    # path('list/', list, name='list'),
    # path('list/<int:pk>', detail, name="detail"),
    path('list/<int:pk>/delete', delete, name="delete"),
    # path('list/<int:pk>/modify', modify, name="modify"),
    path('input', input, name="input"),
    path('list/', views.IndexView.as_view(), name='list'),
    path('list/<int:pk>', views.DetailView.as_view(), name='detail'),
    path('list/<int:pk>/modify', views.UpdateView.as_view(), name='modify'),
    # path('list/<int:pk>/delete', views.DeleteView.as_view(), name='delete'),

]