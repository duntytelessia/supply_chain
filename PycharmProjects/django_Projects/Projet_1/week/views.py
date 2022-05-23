from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from data.models import Week, CustomUser, Goods, Order, Transaction, Stock
from django.forms import formset_factory, modelformset_factory
from week.forms import ChangeUser_1, ChangeUser

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
    if request.method == 'POST':
        if week == 1:
            f = ChangeUser_1(request.POST, instance=User.objects.get(username__exact=username))
        else:
            f = ChangeUser(request.POST, instance=User.objects.get(username__exact=username))
        if f.is_valid():
            f.save()
            user = User.objects.get(username__exact=username)
            user.save()
            messages.success(request, 'Change effective')
            return HttpResponseRedirect(request.path_info)

    else:
        if week == 1:
            f = ChangeUser_1(instance=User.objects.get(username__exact=username))
        else:
            f = ChangeUser(instance=User.objects.get(username__exact=username))

    context = {
        'week': week,
        'user': user,
        'group': group,
        'f': f,
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
    list_a = []
    dict_a = {}
    keys_a = []

    list_b = []
    dict_b = {}
    keys_b = []

    # form layout
    def formlayout(formset, keys, dict):
        i = 0
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

    for buyer in suppliers_b:
        for good in goods_b:
            id = seller.codename + buyer.codename + good.idG + str(week.week)
            if Transaction.objects.filter(idT__exact=id).exists():
                tran = Transaction.objects.get(idT__exact=id)
            else:
                tran = Transaction(idT=id, sellerT=seller, goods=good, buyerT=buyer, dateT=week)
            tran.save()
            list_b.append(id)
            keys_b.append(buyer.codename + good.idG)

    # form creation
    TransactionFormSet = modelformset_factory(Transaction, fields=['quanT', 'priceT'],
                                              labels={'quanT': 'Q', 'priceT': 'P'}, extra=0)

    if request.method == 'POST':
        if 'submitA' in request.POST:
            formset_a = TransactionFormSet(request.POST, queryset=Transaction.objects.filter(idT__in=list_a))
            if formset_a.is_valid():
                formset_a.save()
                messages.success(request, 'Transaction edited')
                return HttpResponseRedirect(request.path_info)
        if 'submitB' in request.POST:
            formset_b = TransactionFormSet(request.POST, queryset=Transaction.objects.filter(idT__in=list_b))
            if formset_b.is_valid():
                formset_b.save()
                messages.success(request, 'Transaction edited')
                return HttpResponseRedirect(request.path_info)

    else:
        formset_a = TransactionFormSet(queryset=Transaction.objects.filter(idT__in=list_a))
        formset_b = TransactionFormSet(queryset=Transaction.objects.filter(idT__in=list_b))
    context = {
        'suppliers_a': suppliers_a,
        'suppliers_b': suppliers_b,
        'goods_a': goods_a,
        'goods_b': goods_b,
        'week': str(week),
        'dict_a': dict_a,
        'dict_b': dict_b,
        'messages': messages,
    }
    formlayout(formset_a, keys_a, dict_a)
    context.update({'formset_a': formset_a})
    formlayout(formset_b, keys_b, dict_b)
    context.update({'formset_b': formset_b})

    return render(request, 'week/modify_as_controltower.html', context=context)


def suppliers_a(user):
    return (user.groups.first().name == 'Suppliers_A')


@user_passes_test(suppliers_a)
def stock_supp_a(request, week, username):
    goods = Goods.objects.filter(idG__in=['R1', 'R3', 'P1', 'P3'])
    user = User.objects.get(username__exact=username)
    group = user.groups.all().first()
    week = Week.objects.get(week__exact=week)
    list_id = []
    keys = []
    dict_f = {}

    # form layout
    def formlayout(formset, keys, dict):
        i = 0
        for f in formset:
            dict.update({keys[i]: f})
            i += 1

    for good in goods:
        id = user.codename + good.idG + str(week.week)
        if Stock.objects.filter(idS__exact=id).exists():
            stc = Stock.objects.get(idS__exact=id)
        else:
            stc = Stock(idS=id, goods=good, idU=user, dateS=week)
        stc.save()
        list_id.append(id)
        keys.append(good.idG)

    StockFormSet = modelformset_factory(Stock, fields=['quanS', ], labels={'quanS': 'Q', }, extra=0)

    if request.method == 'POST':
        q=request.POST
        formset = StockFormSet(request.POST, queryset=Stock.objects.filter(idS__in=list_id))
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Stock edited')
            return HttpResponseRedirect(request.path_info)
    else:
        formset = StockFormSet(queryset=Stock.objects.filter(idS__in=list_id))

    context = {
        'goods': goods,
        'user': user,
        'group': group,
        'week': week,
        'dict_f': dict_f,
        'formset': formset,
    }
    formlayout(formset, keys, dict_f)
    context.update({'formset': formset})
    return render(request, 'week/stock_supp_a.html', context=context)


@user_passes_test(suppliers_a)
def buy_supp_a(request, week, username):
    pass

def notallowed(request):
    return render(request, 'week/notallowed.html')