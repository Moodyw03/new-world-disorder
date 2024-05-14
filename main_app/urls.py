"""
URL configuration for first project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path ,include
from .views import proxy_to_external_api
from .views import get_states_for_country
from .views import send_order_to_printful

from .views import payment_form
from .views import place__cart_order

from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.list_printful_products, name='list_printful_products'),
     path('', include('login.urls')),
     path('ch/',views.Home,name='ch_page'),

    path('product/<int:productId>/', views.product_detail, name='product-detail'),
     path('place-order/', views.place_order, name='place_order'),
     path('place__cart_order/', views.place__cart_order, name='place__cart_order'),
      path('api/proxy/countries/', proxy_to_external_api, name='proxy_countries'),
       path('api/proxy/states/<str:country_code>/', get_states_for_country, name='get_states_for_country'),
        path('order_history/', views.view_order_history, name='view_order_history'),

        path('payment-form/', payment_form, name='payment_form'),
        path('cart_confirm_payment/', views.cart_confirm_payment, name='cart_confirm_payment'),

            path('', views.HomePageView.as_view(), name='home'),
            path('config/', views.stripe_config),
            path('create-checkout-session/', views.create_checkout_session),
            path('create_checkout_session_cart/', views.create_checkout_session_cart),
            path('success/', views.SuccessView.as_view()),
            path('cancelled/', views.CancelledView.as_view()),
            path('webhook/', views.stripe_webhook),
             path('send_order_to_printful/', send_order_to_printful, name='send_order_to_printful'),
             path('send_order_to_printful_using_cart/', views.send_order_to_printful_using_cart, name='send_order_to_printful_using_cart'),

]
