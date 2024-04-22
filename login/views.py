from collections import UserDict
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from .forms import RegistrationForm  # Import the RegistrationForm from forms.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required


from django.contrib.auth import authenticate

def user_login(request):
    context = {
        'username_error': '',  # Initialize username_error as an empty string
        'password_error': '',
        'error': ''
    }

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('list_printful_products')
        else:
            # Authentication failed
            context['error'] = 'Invalid Credentials'
            context['username_error'] = 'Invalid Credentials.'  # Set username_error here

    return render(request, 'login/login.html', context)



def user_logout(request):
    logout(request)
    return redirect('list_printful_products')  # Redirect to login page after logout

def user_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Create a new user and save it to the database
            new_user = User.objects.create_user(username=username, email=email, password=password)
            new_user.save()

            return redirect('login')  # Redirect to the login page after successful registration
    else:
        form = RegistrationForm()

    return render(request, 'login/register.html', {'form': form})
def user_profile(request):
    return render(request, 'login/profile.html', {'user': request.user})

@csrf_exempt
@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        
        # Update user object
        user.username = username
        user.email = email
        user.save()

        return JsonResponse({'status': 'success', 'message': 'Profile updated successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)








   