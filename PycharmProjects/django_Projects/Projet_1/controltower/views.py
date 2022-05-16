from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from controltower.forms import GroupChangeForm

User = get_user_model()


@user_passes_test(lambda u: u.is_superuser)
def interface(request):
    all_users = User.objects.all()
    count_has_group, count_validate = 0, 0
    for u in all_users:
        if u.groups.all().exists():
            count_has_group += 1
        if u.validate:
            count_validate += 1
    can_begin = (count_has_group == count_validate)

    context = {
        'all_users': all_users,
        'can_begin': can_begin,
    }
    return render(request, 'controltower/interface.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def change_group(request, username):
    if request.method == 'POST':
        f = GroupChangeForm(request.POST, instance=User.objects.get(username__exact=username))
        if f.is_valid():
            f.save()
            messages.success(request, 'Group changed successfully')
            return redirect('/controltower')

    else:
        f = GroupChangeForm(request.POST, instance=User.objects.get(username__exact=username))

    return render(request, 'controltower/changegroup.html', {'form': f, 'username': username})


@user_passes_test(lambda u: u.is_superuser)
def del_user(request, username):
    user = User.objects.get(username__exact=username)
    if not user.is_superuser:
        user.delete()
    return redirect('/controltower')


@user_passes_test(lambda u: u.is_superuser)
def valid(request):
    all_users = User.objects.all()

    suppliers_a = User.objects.filter(groups__name__exact='Suppliers_A')
    i = 0
    for user in suppliers_a:
        i += 1
        user.codename = 'SA'+str(i)
        user.save()

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

    context = {
        'all_users': all_users,
    }

    return render(request, 'controltower/valid.html', context=context)
