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
    if has_group:
        group = request.user.groups.all().first()
    else:
        group = ''
    context = {
        'weeks': weeks,
        'has_group': has_group,
    }
    if request.user.is_superuser:
        return render(request, 'week/week.html', context=context)
    else:
        return redirect('/week/'+str(last_week.week)+'/'+group.name+'/'+request.user.username)





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

    distributors = User.objects.filter(groups__name__exact='Distributors')
    goods_a1 = Goods.objects.filter(idG__in=['F1', 'F2'])
    buyer1 = request.user
    list_a1 = []
    dict_a1 = {}
    keys_a1 = []

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

    for seller in distributors:
        for good in goods_a1:
            id = seller.codename + buyer1.codename + good.idG + str(week.week)
            if Order.objects.filter(idO__exact=id).exists():
                order = Order.objects.get(idO__exact=id)
            else:
                order = Order(idO=id, sellerO=seller, goods=good, buyerO=buyer1, dateO=week)
            order.save()
            list_a1.append(id)
            keys_a1.append(seller.codename + good.idG)


    # form creation
    TransactionFormSet = modelformset_factory(Transaction, fields=['quanT', 'priceT'],
                                              labels={'quanT': 'Q', 'priceT': 'P'}, extra=0)
    OrderFormSet = modelformset_factory(Order, fields=['quanO'],
                                              labels={'quanO': 'Q'}, extra=0)

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
        if 'submitA1' in request.POST:
            formset_a1 = OrderFormSet(request.POST, queryset=Order.objects.filter(idO__in=list_a1))
            if formset_a1.is_valid():
                formset_a1.save()
                messages.success(request, 'Order edited')
                return HttpResponseRedirect(request.path_info)


    else:
        formset_a = TransactionFormSet(queryset=Transaction.objects.filter(idT__in=list_a))
        formset_b = TransactionFormSet(queryset=Transaction.objects.filter(idT__in=list_b))
        formset_a1 = OrderFormSet(queryset=Order.objects.filter(idO__in=list_a1))
    context = {
        'suppliers_a': suppliers_a,
        'suppliers_b': suppliers_b,
        'goods_a': goods_a,
        'goods_b': goods_b,
        'week': str(week),
        'dict_a': dict_a,
        'dict_b': dict_b,
        'messages': messages,
        'distributors': distributors,
        'goods_a1': goods_a1,
        'dict_a1': dict_a1,
    }
    formlayout(formset_a, keys_a, dict_a)
    context.update({'formset_a': formset_a})
    formlayout(formset_b, keys_b, dict_b)
    context.update({'formset_b': formset_b})
    formlayout(formset_a1, keys_a1, dict_a1)
    context.update({'formset_a1': formset_a1})


    return render(request, 'week/modify_as_controltower.html', context=context)


def suppliers_a(user):
    return (user.groups.first().name == 'Suppliers_A')

@user_passes_test(suppliers_a)
def supp_a(request, week, username):
    # initializations
    goods = Goods.objects.filter(idG__in=['R1', 'R3', 'P1', 'P3'])
    raw_goods = Goods.objects.filter(idG__in=['R1', 'R3'])
    user = User.objects.get(username__exact=username)
    group = user.groups.all().first()
    week = Week.objects.get(week__exact=week)
    ids_stock, ids_buy = [], []
    keys_stock, keys_buy = [], []
    dict_stock, dict_buy = {}, {}
    dict_info_buy = {}

    # form layout
    def formlayout(formset, keys, dict):
        i = 0
        for f in formset:
            dict.update({keys[i]: f})
            i += 1

    # create stock
    for good in goods:
        id = user.codename + good.idG + str(week.week)
        if Stock.objects.filter(idS__exact=id).exists():
            stc = Stock.objects.get(idS__exact=id)
        else:
            stc = Stock(idS=id, goods=good, idU=user, dateS=week)
        stc.save()
        ids_stock.append(id)
        keys_stock.append(good.idG)

    # validate transaction
    for good in raw_goods:
        id = 'A' + user.codename + good.idG + str(week.week)
        ids_buy.append(id)
        keys_buy.append(good.idG)
        dict_info_buy.update({good.idG: Transaction.objects.get(idT__exact=id)})

    # formset creation
    StockFormSet = modelformset_factory(Stock, fields=['quanS', ], labels={'quanS': 'Q', }, extra=0)
    BuyFormSet = modelformset_factory(Transaction, fields=['verifiedT', ], labels={'verifiedT': 'confirm'}, extra=0)

    if request.method == 'POST':
        if 'submitS' in request.POST:
            formset_stock = StockFormSet(request.POST, queryset=Stock.objects.filter(idS__in=ids_stock))
            if formset_stock.is_valid():
                formset_stock.save()
                messages.success(request, 'Stock edited')
                return HttpResponseRedirect(request.path_info)
        if 'submitB' in request.POST:
            formset_buy = BuyFormSet(request.POST, queryset=Transaction.objects.filter(idT__in=ids_buy))
            if formset_buy.is_valid():
                formset_buy.save()
                messages.success(request, 'Stock edited')
                return HttpResponseRedirect(request.path_info)
        if 'submitV' in request.POST:
            if week.week == 1:
                formset_validate = ChangeUser_1(request.POST, instance=User.objects.get(username__exact=username))
            else:
                formset_validate = ChangeUser(request.POST, instance=User.objects.get(username__exact=username))
            if formset_validate.is_valid():
                formset_validate.save()
                user = User.objects.get(username__exact=username)
                user.save()
                messages.success(request, 'Change effective')
                return HttpResponseRedirect(request.path_info)
    else:
        formset_stock = StockFormSet(queryset=Stock.objects.filter(idS__in=ids_stock))
        formset_buy = BuyFormSet(queryset=Transaction.objects.filter(idT__in=ids_buy))
        if week.week == 1:
            form_validate = ChangeUser_1(instance=User.objects.get(username__exact=username))
        else:
            form_validate = ChangeUser(instance=User.objects.get(username__exact=username))

    context = {
        'goods': goods,
        'raw_goods': raw_goods,
        'user': user,
        'group': group,
        'week': week,
        'dict_info_buy': dict_info_buy,
        'dict_stock': dict_stock,
        'dict_buy': dict_buy,
        'formset_stock': formset_stock,
        'formset_buy': formset_buy,
        'form_validate': form_validate,
    }
    formlayout(formset_stock, keys_stock, dict_stock)
    formlayout(formset_buy, keys_buy, dict_buy)

    return render(request, 'week/supp_a.html', context=context)


def notallowed(request):
    return render(request, 'week/notallowed.html')