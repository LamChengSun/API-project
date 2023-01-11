from django.urls import path
from .import views

urlpatterns = [
    path('',views.home,name='home'),
    path('index', views.index, name='index'),
    path('compare', views.compare, name='compare'),
    path('graph', views.submap, name='submap'),
    path('bar-graph/', views.show_bar_graph, name='show_bar_graph'),
    path('historical-bar-graph/', views.show_historical_bar_graph, name='show_historical_bar_graph'),
]
