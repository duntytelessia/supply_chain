from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, UserChangeForm

User = get_user_model()

@login_required
def profile(request):
    has_group = request.user.groups.all().exists()
    return render(request, 'data/profile.html', context={'has_group': has_group})


def index(request):
    suppliers = User.objects.filter(groups__exact=1)
    s_count = User.objects.filter(groups__exact=1).count()

    factories = User.objects.filter(groups__exact=2)
    f_count = User.objects.filter(groups__exact=2).count()

    warehouses = User.objects.filter(groups__exact=3)
    w_count = User.objects.filter(groups__exact=3).count()

    logistics = User.objects.filter(groups__exact=4)
    l_count = User.objects.filter(groups__exact=4).count()

    distributors = User.objects.filter(groups__exact=5)
    d_count = User.objects.filter(groups__exact=5).count()

    all = s_count + f_count + w_count + l_count + d_count

    context = {
        'suppliers': suppliers,
        's_count': s_count,
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
