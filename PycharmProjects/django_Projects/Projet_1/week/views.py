from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from data.models import Week, CustomUser, Goods, Order, Transaction, Stock, Worker, Path
from django.forms import formset_factory, modelformset_factory
from week.forms import *
from week.forms import ChangeUser_1, ChangeUser, WorkerForm
from django.db.models import Sum

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
        return redirect('/week/'+str(last_week.week)+'/'+request.user.username)


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

def actorL(request, week, username):

    # initializations
    user = User.objects.get(username__exact=username)
    group = user.groups.all().first()
    week = Week.objects.get(week__exact=week)
    first_week = (week.week == 1)
    info_user = InfoUser.objects.get(user=user, date=week)
    logistics = User.objects.filter(groups__name__exact='Logistics')
    userr = request.user
    worker = Worker.objects.get(dateW=week)
    eff = worker.eff
    sal = worker.sal
    numT = info_user.numT
    cap = userr.maxT + numT * eff

    if group.name == 'Logistics':
        quan = Transaction.objects.filter(idT__endswith=userr.codename, dateT=week).aggregate(Sum('quanT'))
    else:
        quan = Transaction.objects.filter(sellerT__exact=userr).aggregate(Sum('quanT'))
    quann = quan.get('quanT__sum')
    if quann == None:
        quann = 0


    if group.name == 'Logistics':

        goods_sales = Goods.objects.filter(idG__in=['F1', 'F2'])
        seller_sales = User.objects.filter(groups__name__exact='Warehouses')
        buyer_sales = User.objects.filter(groups__name__exact='Distributors')
        ids_paths, ids_sales = [], []
        keys_paths, keys_sales = [], []
        dict_paths, dict_sales = {}, {}
        dict_info_paths, dict_info_sales = {}, {}

        def formlayout(formset, keys, dict):
            i = 0
            for f in formset:
                dict.update({keys[i]: f})
                i += 1

        for seller in seller_sales:
            for buyer in buyer_sales:
                #paths
                id_p = seller.codename + buyer.codename + user.codename + str(week.week)
                path = Path.objects.get(idP=id_p)
                dict_info_paths.update({seller.codename + buyer.codename: path})
                ids_paths.append(id_p)
                keys_paths.append(seller.codename + buyer.codename)
                if path.chosenP:
                    for good in goods_sales:
                        # transactions
                        id_t = seller.codename + buyer.codename + good.idG + str(week.week)
                        id_o = seller.codename + buyer.codename + good.idG + str(week.week - 1)
                        tran_exists = Transaction.objects.filter(idT=id_t).exists()
                        order_exists = Order.objects.filter(idO=id_o).exists()
                        if tran_exists and order_exists:
                            order = Order.objects.get(idO__exact=id_o)
                            dict_info_sales.update({seller.codename + buyer.codename + good.idG: order})
                            ids_sales.append(id_t)
                            keys_sales.append(seller.codename + buyer.codename + good.idG)

        SalesFormSet = modelformset_factory(Transaction, fields=['quanT', ], formset=BaseSalesLFormset,
                                            labels={'quanT': 'Q'}, extra=0)
        PathsFormSet = modelformset_factory(Path, fields=['priceP', ], labels={'priceP': 'Price'}, extra=0)

        formset_sales = SalesFormSet(user=user, week=week, queryset=Transaction.objects.filter(idT__in=ids_sales))
        formset_paths = PathsFormSet(queryset=Path.objects.filter(idP__in=ids_paths))
        if week.week == 1:
            form_validate = ChangeUser_1(instance=User.objects.get(username__exact=username))

        f_w = WorkerForm(instance=info_user)
        i_u = ChangeInfoUser(instance=info_user)
        if request.method == 'POST':
            check = True
            if 'submitP' in request.POST:
                formset_paths = PathsFormSet(request.POST, queryset=Path.objects.filter(idP__in=ids_paths))
                if formset_paths.is_valid():
                    formset_paths.save()
                    messages.success(request, 'Paths Edited')
                    return HttpResponseRedirect(request.path_info)
            if 'submitA' in request.POST:
                formset_sales = SalesFormSet(user, week, request.POST, queryset=Transaction.objects.filter(idT__in=ids_sales))
                if formset_sales.is_valid():
                    formset_sales.save()
                    messages.success(request, 'Validated')
                    user.validate = True
                    user.save()
                    return HttpResponseRedirect(request.path_info)
                else:
                    messages.error(request,
                                   'Sth is wrong.')
            if 'submitV' in request.POST:
                if week.week == 1:
                    form_validate = ChangeUser_1(request.POST, instance=User.objects.get(username__exact=username))
                if form_validate.is_valid():
                    form_validate.save()
                    user = User.objects.get(username__exact=username)
                    user.save()
                    messages.success(request, 'Change effective')
                    return HttpResponseRedirect(request.path_info)
            if 'submitW' in request.POST:
                f_w = WorkerForm(request.POST, instance=info_user)  # changes group
                if f_w.is_valid():
                    f_w.save()
                    messages.success(request, 'Worker number info changed')
                    return HttpResponseRedirect(request.path_info)
            if 'submitI' in request.POST:
                i_u = ChangeInfoUser(request.POST, instance=info_user)
                if i_u.is_valid():
                    i_u.save()
                    messages.success(request, 'User Info Changed')
                    return HttpResponseRedirect(request.path_info)
        else:
            f_w = WorkerForm(instance=info_user)
            check = False
        formlayout(formset_sales, keys_sales, dict_sales)
        formlayout(formset_paths, keys_paths, dict_paths)


        context = {
            'user': user,
            'group': group,
            'week': str(week),
            'first_week': first_week,
            'goods_sales': goods_sales,
            'buyer_sales': buyer_sales,
            'seller_sales': seller_sales,
            'dict_sales': dict_sales,
            'dict_info_sales': dict_info_sales,
            'formset_sales': formset_sales,
            'keys_sales': keys_sales,
            'dict_paths': dict_paths,
            'dict_info_paths': dict_info_paths,
            'formset_paths': formset_paths,
            'keys_paths': keys_paths,
            'cap': cap,
            'quann': quann,
            'eff': eff,
            'sal': sal,
            'numT': numT,
            'f_w': f_w,
            'check': check,
            'i_u': i_u,
            'info_user': info_user,
        }
        if week.week == 1:
            context.update({'form_validate': form_validate})
        return render(request, 'week/lo.html', context=context)

def actor(request, week, username):

    # initializations
    user = User.objects.get(username__exact=username)
    group = user.groups.all().first()
    week = Week.objects.get(week__exact=week)
    first_week = (week.week == 1)
    logistics = User.objects.filter(groups__name__exact='Logistics')
    nb_distributors = User.objects.filter(groups__name__exact='Distributors').count()
    info_user = InfoUser.objects.get(user=user, date=week)
    userr = request.user
    worker = Worker.objects.get(dateW=week)
    eff = worker.eff
    sal = worker.sal
    numT = info_user.numT
    cap = userr.maxT + numT * eff

    quan = Transaction.objects.filter(sellerT__exact=userr).aggregate(Sum('quanT'))
    quann = quan.get('quanT__sum')
    if quann == None:
        quann = 0


    # get logistics out of this page
    if group.name == 'Logistics':
        return redirect('/week/' + str(week)+'/'+user.username+'/L')
    if group.name == 'Suppliers_A':
        goods_stock = Goods.objects.filter(idG__in=['R1', 'R3', 'P1', 'P3'])
        goods_buy = Goods.objects.filter(idG__in=['R1', 'R3'])
        seller_buy = User.objects.filter(username__exact='admin')
        buyer_buy = request.user
        goods_sales = Goods.objects.filter(idG__in=['P1', 'P3'])
        seller_sales = request.user
        buyer_sales = User.objects.filter(groups__name__exact='Factories')
    elif group.name == 'Suppliers_B':
        goods_stock = Goods.objects.filter(idG__in=['R2', 'R4', 'P2', 'P4'])
        goods_buy = Goods.objects.filter(idG__in=['R2', 'R4'])
        seller_buy = User.objects.filter(username__exact='admin')
        buyer_buy = request.user
        goods_sales = Goods.objects.filter(idG__in=['P2', 'P4'])
        seller_sales = request.user
        buyer_sales = User.objects.filter(groups__name__exact='Factories')
    elif group.name == 'Factories':
        goods_stock = Goods.objects.filter(idG__in=['P1', 'P2', 'P3', 'P4', 'F1', 'F2'])
        goods_buy = Goods.objects.filter(idG__in=['P1', 'P2', 'P3', 'P4'])
        seller_buy = User.objects.filter(groups__name__startswith='Supplier')
        goods_buy_1 = Goods.objects.filter(idG__in=['P1', 'P3'])
        seller_buy_1 = User.objects.filter(groups__name__exact='Suppliers_A')
        goods_buy_2 = Goods.objects.filter(idG__in=['P2', 'P4'])
        seller_buy_2 = User.objects.filter(groups__name__exact='Suppliers_B')
        buyer_buy = request.user
        goods_sales = Goods.objects.filter(idG__in=['F1', 'F2'])
        seller_sales = request.user
        buyer_sales = User.objects.filter(groups__name__exact='Warehouses')
        ids_order_1, ids_order_2, keys_order_1, keys_order_2, dict_order_1, dict_order_2 = [], [], [], [], {}, {}
        ids_buy_1, keys_buy_1, dict_info_buy_1, ids_buy_2, keys_buy_2, dict_info_buy_2, dict_buy_1, dict_buy_2 = [], [], {}, [], [], {}, {}, {}
    elif group.name == 'Warehouses':
        goods_stock = Goods.objects.filter(idG__in=['F1', 'F2'])
        goods_buy = Goods.objects.filter(idG__in=['F1', 'F2'])
        seller_buy = User.objects.filter(groups__name__exact='Factories')
        buyer_buy = request.user
        goods_sales = Goods.objects.filter(idG__in=['F1', 'F2'])
        seller_sales = request.user
        buyer_sales = User.objects.filter(groups__name__exact='Distributors')

    elif group.name == 'Distributors':
        goods_stock = Goods.objects.filter(idG__in=['F1', 'F2'])
        goods_buy = Goods.objects.filter(idG__in=['F1', 'F2'])
        seller_buy = User.objects.filter(groups__name__exact='Warehouses')
        buyer_buy = request.user
        goods_sales = Goods.objects.filter(idG__in=['F1', 'F2'])
        seller_sales = request.user
        buyer_sales = User.objects.filter(username__exact='admin')
    ids_stock, ids_buy, ids_order, ids_sales = [], [], [], []
    keys_stock, keys_buy, keys_order, keys_sales, keys_path = [], [], [], [], []
    dict_stock, dict_buy, dict_order, dict_sales, dict_path = {}, {}, {}, {}, {}
    dict_info_buy = {}
    dict_info_sales = {}
    dict_info_transport = {}
    dict_info_path = {}
    initial = []
    supp = (group.name == 'Suppliers_A' or group.name == 'Suppliers_B')
    fact = (group.name == 'Factories')
    ware = (group.name == 'Warehouses')
    dist = (group.name == 'Distributors')

    # form layout
    def formlayout(formset, keys, dict):
        i = 0
        for f in formset:
            dict.update({keys[i]: f})
            i += 1

    # create stock
    for good in goods_stock:
        id = user.codename + good.idG + str(week.week)
        if Stock.objects.filter(idS__exact=id).exists():
            stc = Stock.objects.get(idS__exact=id)
        else:
            stc = Stock(idS=id, goods=good, idU=user, dateS=week)
        stc.save()
        ids_stock.append(id)
        keys_stock.append(good.idG)

    # validate transaction
    if group.name == "Factories":
        for good in goods_buy_1:
            for seller in seller_buy_1:
                id = seller.codename + buyer_buy.codename + good.idG + str(week.week)
                if Transaction.objects.filter(idT__exact=id).exists():
                    tran_1 = Transaction.objects.get(idT__exact=id)
                else:
                    tran_1 = Transaction(idT=id, sellerT=seller, goods=good, buyerT=buyer_buy, dateT=week)
                tran_1.save()
                ids_buy_1.append(id)
                keys_buy_1.append(seller.codename + good.idG)
                dict_info_buy_1.update({seller.codename + good.idG: Transaction.objects.get(idT__exact=id)})
        for good in goods_buy_2:
            for seller in seller_buy_2:
                id = seller.codename + buyer_buy.codename + good.idG + str(week.week)
                if Transaction.objects.filter(idT__exact=id).exists():
                    tran_2 = Transaction.objects.get(idT__exact=id)
                else:
                    tran_2 = Transaction(idT=id, sellerT=seller, goods=good, buyerT=buyer_buy, dateT=week)
                tran_2.save()
                ids_buy_2.append(id)
                keys_buy_2.append(seller.codename + good.idG)
                dict_info_buy_2.update({seller.codename + good.idG: Transaction.objects.get(idT__exact=id)})
        ids_buy = ids_buy_1 + ids_buy_2
        keys_buy = keys_buy_1 + keys_buy_2
        dict_info_buy = dict_info_buy_1 | dict_info_buy_2
    else:
        for good in goods_buy:
            for seller in seller_buy:
                id = seller.codename + buyer_buy.codename + good.idG + str(week.week)
                if Transaction.objects.filter(idT__exact=id).exists():
                    tran = Transaction.objects.get(idT__exact=id)
                else:
                    tran = Transaction(idT=id, sellerT=seller, goods=good, buyerT=buyer_buy, dateT=week)
                tran.save()
                ids_buy.append(id)
                keys_buy.append(seller.codename + good.idG)
                dict_info_buy.update({seller.codename + good.idG: Transaction.objects.get(idT__exact=id)})

    # create order
    if group.name == "Factories":
        for seller in seller_buy_1:
            for good in goods_buy_1:
                id = seller.codename + buyer_buy.codename + good.idG + str(week.week)
                if Order.objects.filter(idO__exact=id).exists():
                    order_1 = Order.objects.get(idO__exact=id)
                else:
                    order_1 = Order(idO=id, sellerO=seller, goods=good, buyerO=buyer_buy, dateO=week)
                order_1.save()
                ids_order_1.append(id)
                keys_order_1.append(seller.codename + good.idG)
        for seller in seller_buy_2:
            for good in goods_buy_2:
                id = seller.codename + buyer_buy.codename + good.idG + str(week.week)
                if Order.objects.filter(idO__exact=id).exists():
                    order_2 = Order.objects.get(idO__exact=id)
                else:
                    order_2 = Order(idO=id, sellerO=seller, goods=good, buyerO=buyer_buy, dateO=week)
                order_2.save()
                ids_order_2.append(id)
                keys_order_2.append(seller.codename + good.idG)
        ids_order = ids_order_1 + ids_order_2
        keys_order = keys_order_1 + keys_order_2
    elif group.name != 'Suppliers_A' or group.name != 'Suppliers_B':
        for seller in seller_buy:
            for good in goods_buy:
                id = seller.codename + buyer_buy.codename + good.idG + str(week.week)
                if Order.objects.filter(idO__exact=id).exists():
                    order = Order.objects.get(idO__exact=id)
                else:
                    order = Order(idO=id, sellerO=seller, goods=good, buyerO=buyer_buy, dateO=week)
                order.save()
                ids_order.append(id)
                keys_order.append(seller.codename + good.idG)

    # create transaction
    for buyer in buyer_sales:
        for good in goods_sales:
            id = seller_sales.codename + buyer.codename + good.idG + str(week.week)
            id_order = seller_sales.codename + buyer.codename + good.idG + str(week.week - 1)
            order_exists = Order.objects.filter(idO=id_order).exists()
            if Transaction.objects.filter(idT__exact=id).exists():
                tran = Transaction.objects.get(idT__exact=id)
            else:
                tran = Transaction(idT=id, sellerT=seller_sales, goods=good, buyerT=buyer, dateT=week)
            tran.save()
            ids_sales.append(id)
            keys_sales.append(buyer.codename + good.idG)
            if order_exists:
                order = Order.objects.get(idO__exact=id_order)
                dict_info_sales.update({buyer.codename + good.idG: order})
            else:
                dict_info_sales.update({buyer.codename + good.idG: ' '})

    # initialize paths
    path_sellers = []
    path_buyers = []
    if group.name == 'Warehouses':
        for buyer in buyer_sales:
            initialized = False
            for logic in logistics:
                id = seller_sales.codename + buyer.codename + logic.codename + str(week.week)
                path = Path.objects.get(idP__exact=id)
                dict_info_path.update({buyer.codename + logic.codename: path})
                if path.chosenP:
                    initial.append({'chose': path.logicP})
                    initialized = True
            if not initialized:
                initial.append({'chose': None})
            path_sellers.append(user)
            path_buyers.append(buyer)
            keys_path.append(buyer.codename)

    # create formsets
    if group.name == "Factories":
        StockFormSet = modelformset_factory(Stock, fields=['quanS', ], labels={'quanS': 'Q', }, extra=0)
        BuyFormSet_1 = modelformset_factory(Transaction, fields=['verifiedT', ], labels={'verifiedT': 'confirm'},
                                            extra=0)
        BuyFormSet_2 = modelformset_factory(Transaction, fields=['verifiedT', ], labels={'verifiedT': 'confirm'},
                                            extra=0)
        OrderFormSet_1 = modelformset_factory(Order, fields=['quanO'],
                                              labels={'quanO': 'Q'}, extra=0)
        OrderFormSet_2 = modelformset_factory(Order, fields=['quanO'],
                                              labels={'quanO': 'Q'}, extra=0)
        SalesFormSet = modelformset_factory(Transaction, formset=BaseSalesFormset, fields=['quanT', 'priceT'],
                                            labels={'quanT': 'Q', 'priceT': 'P'}, extra=0)
    else:

        StockFormSet = modelformset_factory(Stock, fields=['quanS', ], labels={'quanS': 'Q', }, extra=0)
        BuyFormSet = modelformset_factory(Transaction, fields=['verifiedT', ], labels={'verifiedT': 'confirm'}, extra=0)
        OrderFormSet = modelformset_factory(Order, fields=['quanO'],
                                            labels={'quanO': 'Q'}, extra=0)
        SalesFormSet = modelformset_factory(Transaction, formset=BaseSalesFormset,
                                            fields=['quanT', 'priceT'],
                                            labels={'quanT': 'Q', 'priceT': 'P'},
                                            extra=0)
    LogicFormset = formset_factory(LogicForm, formset=RequiredFormSet, extra=0)


    # forms
    if group.name == "Factories":
        formset_buy_1 = BuyFormSet_1(queryset=Transaction.objects.filter(idT__in=ids_buy_1))
        formset_buy_2 = BuyFormSet_2(queryset=Transaction.objects.filter(idT__in=ids_buy_2))
        formset_order_1 = OrderFormSet_1(queryset=Order.objects.filter(idO__in=ids_order_1))
        formset_order_2 = OrderFormSet_2(queryset=Order.objects.filter(idO__in=ids_order_2))
    else:
        formset_buy = BuyFormSet(queryset=Transaction.objects.filter(idT__in=ids_buy))
        formset_order = OrderFormSet(queryset=Order.objects.filter(idO__in=ids_order))
    formset_stock = StockFormSet(queryset=Stock.objects.filter(idS__in=ids_stock))
    formset_sales = SalesFormSet(queryset=Transaction.objects.filter(idT__in=ids_sales))
    formset_logic = LogicFormset(initial=initial)
    if week.week == 1:
        form_validate = ChangeUser_1(instance=User.objects.get(username__exact=username))
    else:
        form_validate = ChangeUser(instance=User.objects.get(username__exact=username))

    f_w = WorkerForm(instance=info_user)
    i_u = ChangeInfoUser(instance=info_user)

    if request.method == 'POST':
        if 'submitS' in request.POST:
            formset_stock = StockFormSet(request.POST, queryset=Stock.objects.filter(idS__in=ids_stock))
            if formset_stock.is_valid():
                formset_stock.save()
                messages.success(request, 'Stock edited')
                return HttpResponseRedirect(request.path_info)
        if group.name == "Factories":
            if 'submitB_1' in request.POST:
                formset_buy_1 = BuyFormSet_1(request.POST, queryset=Transaction.objects.filter(idT__in=ids_buy_1))
                if formset_buy_1.is_valid():
                    formset_buy_1.save()
                    messages.success(request, 'Buys edited')
                    return HttpResponseRedirect(request.path_info)
            if 'submitB_2' in request.POST:
                formset_buy_2 = BuyFormSet_2(request.POST, queryset=Transaction.objects.filter(idT__in=ids_buy_2))
                if formset_buy_2.is_valid():
                    formset_buy_2.save()
                    messages.success(request, 'Buys edited')
                    return HttpResponseRedirect(request.path_info)
            if 'submitO_1' in request.POST:
                formset_order_1 = OrderFormSet_1(request.POST, queryset=Order.objects.filter(idO__in=ids_order_1))
                if formset_order_1.is_valid():
                    formset_order_1.save()
                    messages.success(request, 'Order validated')
                    return HttpResponseRedirect(request.path_info)
            if 'submitO_2' in request.POST:
                formset_order_2 = OrderFormSet_2(request.POST, queryset=Order.objects.filter(idO__in=ids_order_2))
                if formset_order_2.is_valid():
                    formset_order_2.save()
                    messages.success(request, 'Order validated')
                    return HttpResponseRedirect(request.path_info)
        else:
            if 'submitB' in request.POST:
                formset_buy = BuyFormSet(request.POST, queryset=Transaction.objects.filter(idT__in=ids_buy))
                if formset_buy.is_valid():
                    formset_buy.save()
                    messages.success(request, 'Buys edited')
                    return HttpResponseRedirect(request.path_info)
            if 'submitO' in request.POST:
                formset_order = OrderFormSet(request.POST, queryset=Order.objects.filter(idO__in=ids_order))
                if formset_order.is_valid():
                    formset_order.save()
                    messages.success(request, 'Order validated')
                    return HttpResponseRedirect(request.path_info)
        if 'submitA' in request.POST:
            formset_sales = SalesFormSet(request.POST, queryset=Transaction.objects.filter(idT__in=ids_sales))
            if formset_sales.is_valid():
                formset_sales.save()
                messages.success(request, 'Sales edited')
                return HttpResponseRedirect(request.path_info)
            else:
                messages.error(request,
                               'Sales Edit failed. Plz check the stock or the order.')
        if 'submitP' in request.POST:
            formset_logic = LogicFormset(request.POST, initial=initial)
            if formset_logic.is_valid():
                i = 0
                u = formset_logic.cleaned_data
                for form in formset_logic.forms:
                    buyer = User.objects.get(codename__exact=keys_path[i])
                    logic = form.cleaned_data['chose']
                    path = Path.objects.get(sellerP=seller_sales, buyerP=buyer, logicP=logic, dateP=week)
                    all_paths = Path.objects.filter(sellerP=seller_sales, buyerP=buyer, dateP=week)
                    all_other = all_paths.exclude(idP=path.idP)
                    path.chosenP = True
                    path.save()
                    for p in all_other:
                        p.chosenP = False
                        p.save()
                    i += 1
                messages.success(request, 'Paths edited')
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

        if 'submitW' in request.POST:
            f_w = WorkerForm(request.POST, instance=info_user)  # changes group
            if f_w.is_valid():
                f_w.save()
                messages.success(request, 'Worker number info changed')
                return HttpResponseRedirect(request.path_info)
        if 'submitI' in request.POST:
            i_u = ChangeInfoUser(request.POST, instance=info_user)
            if i_u.is_valid():
                i_u.save()
                messages.success(request, 'User Info Changed')
                return HttpResponseRedirect(request.path_info)
    else:
        f_w = WorkerForm(instance=CustomUser.objects.get(username__exact=username))

    # form layout
    formlayout(formset_stock, keys_stock, dict_stock)
    formlayout(formset_sales, keys_sales, dict_sales)
    formlayout(formset_logic, keys_path, dict_path)
    if group.name == "Factories":
        formlayout(formset_buy_1, keys_buy_1, dict_buy_1)
        formlayout(formset_buy_2, keys_buy_2, dict_buy_2)
        formlayout(formset_order_1, keys_order_1, dict_order_1)
        formlayout(formset_order_2, keys_order_2, dict_order_2)
        dict_order = dict_order_1 | dict_order_2
        dict_buy = dict_buy_1 | dict_buy_2
    else:
        formlayout(formset_buy, keys_buy, dict_buy)
        formlayout(formset_order, keys_order, dict_order)

    # context
    context = {
        'user': user,
        'group': group,
        'week': str(week),
        'first_week': first_week,
        'goods_stock': goods_stock,
        'goods_buy': goods_buy,
        'seller_buy': seller_buy,
        'goods_sales': goods_sales,
        'buyer_sales': buyer_sales,
        'dict_stock': dict_stock,
        'dict_buy': dict_buy,
        'dict_order': dict_order,
        'dict_sales': dict_sales,
        'dict_path': dict_path,
        'dict_info_buy': dict_info_buy,
        'dict_info_sales': dict_info_sales,
        'dict_info_transport': dict_info_transport,
        'dict_info_path': dict_info_path,
        'formset_stock': formset_stock,
        'formset_sales': formset_sales,
        'form_validate': form_validate,
        'formset_logic': formset_logic,
        'logistics': logistics,
        'supp': supp,
        'fact': fact,
        'ware': ware,
        'dist': dist,
        'cap': cap,
        'quann': quann,
        'eff': eff,
        'sal': sal,
        'numT': numT,
        'f_w': f_w,
        'i_u': i_u,
        'info_user': info_user,
    }
    if group.name == "Factories":
        context['dict_buy_1'] = dict_buy_1
        context['dict_buy_2'] = dict_buy_2
        context['goods_buy_1'] = goods_buy_1
        context['goods_buy_2'] = goods_buy_2
        context['seller_buy_1'] = seller_buy_1
        context['seller_buy_2'] = seller_buy_2
        context['dict_order_1'] = dict_order_1
        context['dict_order_2'] = dict_order_2
        context['dict_info_buy_1'] = dict_info_buy_1
        context['dict_info_buy_2'] = dict_info_buy_2
        context['formset_buy_1'] = formset_buy_1
        context['formset_buy_2'] = formset_buy_2
        context['formset_order_1'] = formset_order_1
        context['formset_order_2'] = formset_order_2
    else:
        context['formset_buy'] = formset_buy
        context['formset_order'] = formset_order

    return render(request, 'week/actor.html', context=context)

def notallowed(request):
    return render(request, 'week/notallowed.html')