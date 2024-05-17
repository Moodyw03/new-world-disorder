from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import redirect

def user_login(request):
    context = {
        'username_error': '',
        'password_error': '',
        'error': ''
    }

    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        try:
            # Use Q objects for combined query
            user = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))

            # Authenticate user
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                login(request, user)
                return redirect('list_printful_products')
            else:
                context['error'] = 'Invalid Credentials'
                context['password_error'] = 'Invalid Credentials.'
        except User.DoesNotExist:
            context['error'] = 'Invalid Credentials'
            context['username_error'] = 'Invalid Credentials.'

    return render(request, 'login/login.html', context)


def user_logout(request):
    logout(request)
    return redirect('list_printful_products')  # Redirect to the product list page after logout


def user_register(request):
    error_message = None
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                # Create a new user and save it to the database
                new_user = User.objects.create_user(username=username, email=email, password=password)
                new_user.save()
                return redirect('login')  # Redirect to the login page after successful registration
            except IntegrityError:
                error_message = "Username already exists. Please choose a different one."
    else:
        form = RegistrationForm()

    return render(request, 'login/register.html', {'form': form, 'error_message': error_message})


@login_required
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
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return JsonResponse({'status': 'success', 'message': 'Account deleted successfully'}, status=200)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)