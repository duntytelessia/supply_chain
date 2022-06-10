from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from .forms import CustomUserCreationForm, UserChangeForm, ValidationForm

from .models import Goods, Week, Worker

User = get_user_model()


@login_required     # only logged-in users can see this page
def profile(request):   # profile page for logged-in user
    has_group = request.user.groups.all().exists()
    if request.method == 'POST':    # allows the user to validate the group the admin gave to him
        f = ValidationForm(request.POST, instance=request.user)
        if f.is_valid():    # if the information entered in the form is valid
            f.save()    # executes the save function of the form
            messages.success(request, 'Validation complete')
            return redirect('profile')

    else:
        f = ValidationForm(instance=request.user)
    return render(request, 'data/profile.html', context={'has_group': has_group, 'form': f})


def index(request):

    group_exist = Group.objects.all().exists()

    suppliers_a = User.objects.filter(groups__name__exact='Suppliers_A')    # all the users in the group suppliers_a
    s_a_count = User.objects.filter(groups__name__exact='Suppliers_A').count()  # how many users in the group

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

    all = s_a_count + s_b_count + f_count + w_count + l_count + d_count     # how many users in total

    week_exist = Week.objects.all().exists()

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
        'group_exist': group_exist,
        'week_exist': week_exist,
    }
    return render(request, 'data/index.html', context = context)


def succes(request):    # when registration is complete
    return render(request, 'data/succes.html')


def register(request):  # register a new user
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
def modify(request):    # modify the information of a user
    if request.method == 'POST':
        f = UserChangeForm(request.POST, instance=request.user)
        if f.is_valid():
            f.save()
            messages.success(request, 'Information changed successfully')
            return redirect('modify')

    else:
        f = UserChangeForm(instance=request.user)

    return render(request, 'data/infos.html', {'form': f})


def initialize(request):
    if not Group.objects.all().exists():  # creates all groups that are needed
        suppliers_a = Group(name='Suppliers_A')
        suppliers_a.save()
        suppliers_b = Group(name='Suppliers_B')
        suppliers_b.save()
        factories = Group(name='Factories')
        factories.save()
        warehouses = Group(name='Warehouses')
        warehouses.save()
        logistics = Group(name='Logistics')
        logistics.save()
        distributors = Group(name='Distributors')
        distributors.save()

    if not Goods.objects.all().exists():
        good_mp1 = Goods(idG='R1', nameG='raw beef', durG=3)
        good_mp1.save()
        good_mp2 = Goods(idG='R2', nameG='pepper', durG=3)
        good_mp2.save()
        good_mp3 = Goods(idG='R3', nameG='raw pork', durG=5)
        good_mp3.save()
        good_mp4 = Goods(idG='R4', nameG='sauce', durG=5)
        good_mp4.save()
        good_m1 = Goods(idG='P1', nameG='beef', durG=3)
        good_m1.save()
        good_m2 = Goods(idG='P2', nameG='beed sauce', durG=3)
        good_m2.save()
        good_m3 = Goods(idG='P3', nameG='pork', durG=5)
        good_m3.save()
        good_m4 = Goods(idG='P4', nameG='pork sauce', durG=5)
        good_m4.save()
        good_f1 = Goods(idG='F1', nameG='Beef jerky', durG=7)
        good_f1.save()
        good_f2 = Goods(idG='F2', nameG='juicy pork', durG=7)
        good_f2.save()

    if not User.objects.all().exists():
        User.objects.create_user(username='admin',
                                 email='wenjie.liu1002@gmail.com',
                                 password='1234',
                                 is_staff=True,
                                 is_active=True,
                                 is_superuser=True
                                 )
        User.objects.create_user(username='U1',
                                 email='s1@s.com',
                                 password='1234',
                                 is_active=True,
                                 )
        User.objects.create_user(username='U2',
                                 email='s2@s.com',
                                 password='1234',
                                 is_active=True,
                                 )
        User.objects.create_user(username='U3',
                                 email='f1@f.com',
                                 password='1234',
                                 is_active=True,
                                 )
        User.objects.create_user(username='U4',
                                 email='w1@w.com',
                                 password='1234',
                                 is_active=True,
                                 )
        User.objects.create_user(username='U5',
                                 email='l1@l.com',
                                 password='1234',
                                 is_active=True,
                                 )
        User.objects.create_user(username='U6',
                                 email='d1@d.com',
                                 password='1234',
                                 is_active=True,
                                 )

    return render(request, 'data/initialize.html')