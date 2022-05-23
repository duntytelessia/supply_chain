from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from data.models import Week, CustomUser, Goods, Order, Transaction
from django.forms import formset_factory, modelformset_factory
from week.forms import PriceForm

User = get_user_model()


@login_required
def week(request):
    has_group = request.user.groups.all().exists()
    weeks = Week.objects.all().order_by('week')
    last_week = weeks.last()
    context = {
        'weeks': weeks,
        'has_group': has_group,
    }
    if request.user.is_superuser:
        return render(request, 'week/week.html', context=context)
    else:
        return redirect('/week/'+str(last_week.week)+'/'+request.user.username)


def infos(request, week, username):
    user = User.objects.get(username__exact=username)
    group = user.groups.all().first()

    context = {
        'week': week,
        'user': user,
        'group': group,
    }
    return render(request, 'week/infos.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def modify_as_controltower(request, week):

    # variables initialisations
    suppliers_a = User.objects.filter(groups__name__exact='Suppliers_A')
    suppliers_b = User.objects.filter(groups__name__exact='Suppliers_B')
    goods_a = Goods.objects.filter(idG__in=['R1', 'R3'])
    goods_b = Goods.objects.filter(idG__in=['R2', 'R4'])
    seller = request.user
    week = Week.objects.get(week__exact=week)
    list_a, list_p = [], []
    dict_a, dict_p = {}, {}
    keys_a, keys_p = [], []

    # form layout
    def formlayout(formset, keys, dict):
        i=0
        for f in formset:
            dict.update({keys[i]: f})
            i += 1

    # create or get every transaction we want to modify
    for buyer in suppliers_a:
        for good in goods_a:
            id = seller.codename + buyer.codename + good.idG + str(week.week)
            if Transaction.objects.filter(idT__exact=id).exists():
                tran = Transaction.objects.get(idT__exact=id)
            else:
                tran = Transaction(idT=id, sellerT=seller, goods=good, buyerT=buyer, dateT=week)
            tran.save()
            list_a.append(id)
            keys_a.append(buyer.codename + good.idG)

    # form creation
    TransactionFormSet = modelformset_factory(Transaction, fields=['quanT', 'priceT'],
                                              labels={'quanT': 'Q', 'priceT': 'P'}, extra=0)

    if request.method == 'POST':
        formset_a = TransactionFormSet(request.POST, queryset=Transaction.objects.filter(idT__in=list_a))
        if formset_a.is_valid():
            formset_a.save()
            messages.success(request, 'Transaction edited')
            return HttpResponseRedirect(request.path_info)

    else:
        formset_a = TransactionFormSet(queryset=Transaction.objects.filter(idT__in=list_a))

    formlayout(formset_a, keys_a, dict_a)
    context = {
        'suppliers_a': suppliers_a,
        'suppliers_b': suppliers_b,
        'goods_a': goods_a,
        'goods_b': goods_b,
        'week': str(week),
        'dict_a': dict_a,
        'dict_p': dict_p,
        'messages': messages,
        'formset_a': formset_a,
    }

    return render(request, 'week/modify_as_controltower.html', context=context)


def stock_supp_a(request, week, username):
    return render(request, 'week/stock_supp_a.html')

def notallowed(request):
    return render(request, 'week/notallowed.html')

