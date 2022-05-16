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
    context = {
        'all_users': all_users,
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
