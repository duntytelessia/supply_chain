from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, UserChangeForm, ValidationForm

User = get_user_model()

@login_required
def profile(request):
    has_group = request.user.groups.all().exists()
    if request.method == 'POST':
        f = ValidationForm(request.POST, instance=request.user)
        if f.is_valid():
            f.save()
            messages.success(request, 'Validation complete')
            return redirect('profile')

    else:
        f = ValidationForm(instance=request.user)
    return render(request, 'data/profile.html', context={'has_group': has_group, 'form': f})


def index(request):
    suppliers_a = User.objects.filter(groups__name__exact='Suppliers_A')
    s_a_count = User.objects.filter(groups__name__exact='Suppliers_A').count()

    suppliers_b = User.objects.filter(groups__name__exact='Suppliers_B')
    s_b_count = User.objects.filter(groups__name__exact='Suppliers_B').count()

    factories = User.objects.filter(groups__name__exact='Factories')
    f_count = User.objects.filter(groups__name__exact='Factories').count()

    warehouses = User.objects.filter(groups__name__exact='Warehouses')
    w_count = User.objects.filter(groups__name__exact='Warehouses').count()

    logistics = User.objects.filter(groups__name__exact='Logistics')
    l_count = User.objects.filter(groups__name__exact='Logistics').count()

    distributors = User.objects.filter(groups__name__exact='Distributors')
    d_count = User.objects.filter(groups__name__exact='Distributors').count()

    all = s_a_count + s_b_count + f_count + w_count + l_count + d_count

    context = {
        'suppliers_a': suppliers_a,
        's_a_count': s_a_count,
        'suppliers_b': suppliers_b,
        's_b_count': s_b_count,
        'factories': factories,
        'f_count': f_count,
        'warehouses': warehouses,
        'w_count': w_count,
        'logistics': logistics,
        'l_count': l_count,
        'distributors': distributors,
        'd_count': d_count,
        'all': all,
    }
    return render(request, 'data/index.html', context = context)


def succes(request):
    return render(request, 'data/succes.html')


def register(request):
    if request.method == 'POST':
        f = CustomUserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Account created successfully')
            return redirect('register')

    else:
        f = CustomUserCreationForm()

    return render(request, 'data/register.html', {'form': f})


@login_required
def modify(request):
    if request.method == 'POST':
        f = UserChangeForm(request.POST, instance=request.user)
        if f.is_valid():
            f.save()
            messages.success(request, 'Information changed successfully')
            return redirect('modify')

    else:
        f = UserChangeForm(instance=request.user)

    return render(request, 'data/modify.html', {'form': f})
