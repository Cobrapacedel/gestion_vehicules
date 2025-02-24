from django.urls import path
from payments.views import pay_toll, coinpayments_ipn

urlpatterns = [
    path("pay-toll/<int:vehicle_id>/", pay_toll, name="pay_toll"),
    path("coinpayments/ipn/", coinpayments_ipn, name="coinpayments_ipn"),
    
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

