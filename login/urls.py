# urls.py in the "login" app
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('profile/', views.user_profile, name='profile'),
     path('path/to/update-profile/', views.update_profile, name='update_profile'),
     path('delete_account/', views.delete_account, name='delete_account'),
]