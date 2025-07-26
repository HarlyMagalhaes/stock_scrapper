from django.urls import path
from . import views

urlpatterns = [
    path('details/<str:ticker>/', views.get_details_view, name='get_details'),
    path('yearly_dividends/<str:ticker>/', views.get_yearly_dividends_view, name='get_yearly_dividends'),
    path('monthly_dividends/<str:ticker>/', views.get_monthly_dividends_view, name='get_monthly_dividends'),
    path('accumulated_yearly_dividends/<str:ticker>/<int:years>/', views.get_accumulated_yearly_dividends_view, name='get_accumulated_yearly_dividends'),
    path('accumulated_monthly_dividends/<str:ticker>/<int:months>/', views.get_accumulated_monthly_dividends_view, name='get_accumulated_monthly_dividends'),
]