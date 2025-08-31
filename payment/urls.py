from django.urls import path,include
from . import views


urlpatterns = [
    path('payment_success/', views.payment_success, name='payment_success'),
    path('stripe_success/', views.stripe_success, name='stripe_success'),
    path('payment_failed', views.payment_failed, name='payment_failed'),
    path('checkout/', views.checkout, name='checkout'),
    path('billing_info/', views.billing_info, name='billing_info'),
    path('shipped_dash/', views.shipped_dash, name='shipped_dash'),
    path('not_shipped_dash/', views.not_shipped_dash, name='not_shipped_dash'),
    path('orders/<int:pk>', views.orders, name='orders'),
    path('paypal', include("paypal.standard.ipn.urls")),
    path('submit-email/', views.submit_email, name='submit-email'),
    path('stripe_checkout/', views.stripe_checkout, name='stripe_checkout'),
    path('stripe_payment/', views.stripe_payment, name='stripe_payment'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),

]
