"""RewardsRadar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('welcome/', views.welcome_view, name='welcome'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('product/<int:product_id>/purchase/confirmation/', views.product_purchase_confirmation, name='product_purchase_confirmation'),
    path('process_payment/<int:product_id>/', views.process_payment_view, name='process_payment'),

    # path('products/', views.ProductListView.as_view(), name='product_list'),
    # path('product/<int:product_id>/purchase/confirmation/', views.product_purchase_confirmation, 
    #      name='product_purchase_confirmation'),
    # # path('process_payment/', views.process_payment_view, name='process_payment'),
    # path('process_payment/<int:product_id>/', views.process_payment_view, name='process_payment'),

    path('payment_success/', views.success_page, name='payment_success'),
    path('payment_failure/', views.payment_failure, name='payment_failure'),



    # path('products/', views.products_view, name='products'),
    # path('product/<int:product_id>/', views.product_details, name='product_details'), 
    path('locations/', views.locations_view, name='locations'),
    path('register/', views.CustomerRegistrationView.as_view(), name='customer_registration'),
    path('webhooks/square/', views.webhook_view, name='webhook'),
    path('reward-tier/create/', views.create_reward_tier, name='create_reward_tier'),
    path('reward-tier/list/', views.reward_tier_list, name='reward_tier_list'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('profile/', views.profile_view, name='customer_profile'),
    path('accounts/login/', views.CustomerLoginView.as_view(), name='customer_login'),
]