from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from controltower.forms import GroupChangeForm, GoodChangeForm
from data.models import Goods, Week

User = get_user_model()


@user_passes_test(lambda u: u.is_superuser)     # only admin can access this page
def interface(request):
    has_begun = Week.objects.all().exists()
    all_users = User.objects.all()
    count_has_group, count_validate = 0, 0
    for u in all_users:   # to know if each user with a group has validated
        if u.groups.all().exists():
            count_has_group += 1
        if u.validate:
            count_validate += 1
    can_begin = (count_has_group == count_validate)     # we can start the simulation

    context = {
        'all_users': all_users,
        'can_begin': can_begin,
    }
    if has_begun:
        return redirect('/week')
    else:
        return render(request, 'controltower/interface.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def change_group(request, username):    # username comes from the second part of the url
    if request.method == 'POST':
        f = GroupChangeForm(request.POST, instance=User.objects.get(username__exact=username))  # changes group
        if f.is_valid():
            f.save()
            user = User.objects.get(username__exact=username)  # user needs to validate again after a change of group
            user.validate = False
            user.save()
            messages.success(request, 'Group changed successfully')
            return redirect('/controltower')

    else:
        f = GroupChangeForm(instance=User.objects.get(username__exact=username))

    return render(request, 'controltower/changegroup.html', {'form': f, 'username': username})


@user_passes_test(lambda u: u.is_superuser)
def del_user(request, username):    # username comes from the second part of the url
    user = User.objects.get(username__exact=username)
    if not user.is_superuser:  # you can't delete another admin
        user.delete()
    return redirect('/controltower')


@user_passes_test(lambda u: u.is_superuser)
def edit_good(request, idg):    # idG comes from the second part of the url
    if request.method == 'POST':
        f = GoodChangeForm(request.POST, instance=Goods.objects.get(idG__exact=idg))  # changes group
        if f.is_valid():
            f.save()
            messages.success(request, 'Info changed successfully')
            return redirect('/controltower/valid')

    else:
        f = GoodChangeForm(instance=Goods.objects.get(idG__exact=idg))

    return render(request, 'controltower/editgood.html', {'form': f, 'idG': idg})


@user_passes_test(lambda u: u.is_superuser)
def valid(request):
    all_users = User.objects.all()

    suppliers_a = User.objects.filter(groups__name__exact='Suppliers_A')    # all the users with the role supplier A
    i = 0
    for user in suppliers_a:    # attributes a code in the form SA'i' automatically
        i += 1
        user.codename = 'SA'+str(i)
        user.save()     # important, saves the changes

    suppliers_b = User.objects.filter(groups__name__exact='Suppliers_B')
    i = 0
    for user in suppliers_b:
        i += 1
        user.codename = 'SB'+str(i)
        user.save()

    factories = User.objects.filter(groups__name__exact='Factories')
    i = 0
    for user in factories:
        i += 1
        user.codename = 'F'+str(i)
        user.save()

    warehouses = User.objects.filter(groups__name__exact='Warehouses')
    i = 0
    for user in warehouses:
        i += 1
        user.codename = 'W'+str(i)
        user.save()

    logistics = User.objects.filter(groups__name__exact='Logistics')
    i = 0
    for user in logistics:
        i += 1
        user.codename = 'L'+str(i)
        user.save()

    distributors = User.objects.filter(groups__name__exact='Distributors')
    i = 0
    for user in distributors:
        i += 1
        user.codename = 'D'+str(i)
        user.save()

    goods_r = Goods.objects.filter(idG__contains='R').order_by('idG')
    goods_p = Goods.objects.filter(idG__contains='P').order_by('idG')
    goods_f = Goods.objects.filter(idG__contains='F').order_by('idG')
    context = {
        'all_users': all_users,
        'goods_r': goods_r,
        'goods_p': goods_p,
        'goods_f': goods_f,
    }

    return render(request, 'controltower/valid.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def validate_all(request):
    users = User.objects.all()
    for user in users:
        if user.groups.all().exists():
            user.validate = True
            user.save()

    return redirect('/controltower')


@user_passes_test(lambda u: u.is_superuser)
def begin_simulation(request):
    for user in User.objects.all():
        user.validate = False
        user.save()
    week_1 = Week(week=1)
    week_1.save()

    return render(request, 'controltower/begin_simulation.html')
