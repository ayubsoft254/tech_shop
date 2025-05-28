from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('hardware/', views.HardwareProductListView.as_view(), name='hardware_list'),
    path('hardware/<slug:slug>/', views.HardwareProductDetailView.as_view(), name='hardware_detail'),
    path('software/', views.SoftwareProductListView.as_view(), name='software_list'),
    path('software/<slug:slug>/', views.SoftwareProductDetailView.as_view(), name='software_detail'),
    path('search/', views.SearchResultsView.as_view(), name='search_results'),
]