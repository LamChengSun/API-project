from django.urls import path
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submap/<str:name>/', views.submap, name='submap'),
]
