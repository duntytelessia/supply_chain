from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from data.models import Week, CustomUser, Goods, Order, Transaction
from week.forms import TransactionForm
from django.forms import modelformset_factory

User = get_user_model()


@login_required
def week(request):
    has_group = request.user.groups.all().exists()
    weeks = Week.objects.all()
    context = {
        'weeks': weeks,
        'has_group': has_group,
    }
    return render(request, 'week/week.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def modify_as_controltower(request, week):

    # variables initialisations
    suppliers_a = User.objects.filter(groups__name__exact='Suppliers_A')
    suppliers_b = User.objects.filter(groups__name__exact='Suppliers_B')
    goods_a = Goods.objects.filter(idG__in=['R1', 'R3'])
    goods_b = Goods.objects.filter(idG__in=['R2', 'R4'])
    seller = request.user
    week = Week.objects.get(week__exact=week)
    list = []

    # create or get every transaction we want to modify
    for buyer in suppliers_a:
        for good in goods_a:
            id = seller.codename + buyer.codename + good.idG + str(week.week)
            if Transaction.objects.filter(idT__exact=id).exists():
                tran = Transaction.objects.get(idT__exact=id)
            else:
                tran = Transaction(idT=id, sellerT=seller, goods=good, buyerT=buyer, dateT=week)
            tran.save()
            list.append(id)

    # form creation
    TransactionFormSet = modelformset_factory(Transaction, fields=['quanT'], labels={'quanT': ''}, extra=0)

    if request.method == 'POST':
        test = False
        formset = TransactionFormSet(request.POST or None, queryset=Transaction.objects.filter(idT__in=list))
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Transaction edited')
            return HttpResponseRedirect(request.path_info)

    else:
        formset = TransactionFormSet(queryset=Transaction.objects.filter(idT__in=list))

    context = {
        'suppliers_a': suppliers_a,
        'suppliers_b': suppliers_b,
        'goods_a': goods_a,
        'goods_b': goods_b,
        'week': str(week),
        'messages': messages,
        'formset': formset,
    }

    return render(request, 'week/modify_as_controltower.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def transaction_ct(request, week, codename, idg):

    seller = request.user
    buyer = User.objects.get(codename__exact=codename)
    good = Goods.objects.get(idG__exact=idg)
    week = Week.objects.get(week__exact=week)
    id = seller.codename + buyer.codename + good.idG + str(week.week)
    if Transaction.objects.filter(idT__exact=id).exists():
        tran = Transaction.objects.get(idT__exact=id)
    else:
        tran = Transaction(idT=id, sellerT=seller, buyerT=buyer, dateT=week)
        tran.save()
    if request.method == 'POST':
        f = TransactionForm(request.POST, instance=tran)  # changes group
        if f.is_valid():
            f.save()
            messages.success(request, 'Transaction edited')
            return redirect('/week/'+str(week)+'/controltower/modify')

    else:
        f = TransactionForm(instance=tran)

    context = {
        'id': id,
        'seller': seller,
        'buyer': buyer,
        'good': good,
        'week': week,
        'f': f,
    }
    return render(request, 'week/transaction.html', context=context)


def notallowed(request):
    return render(request, 'week/notallowed.html')

