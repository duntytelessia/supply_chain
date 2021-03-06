from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import user_passes_test
from controltower.forms import GroupChangeForm, GoodChangeForm, WorkersForm
from data.models import Goods, Week, Order, Transaction, Stock, Worker, Path, InfoUser
from django.forms import modelformset_factory
from controltower.forms import *


User = get_user_model()


@user_passes_test(lambda u: u.is_superuser)     # only admin can access this page
def interface(request):
    has_begun = Week.objects.all().exists()
    all_users = User.objects.all()
    count_has_group, count_validate = 0, 0
    weeks = Week.objects.all().order_by('week')
    last_week = weeks.last()
    if has_begun:
        first_week = (last_week.week == 1)
    else:
        first_week = True
    for u in all_users:   # to know if each user with a group has validated
        if u.groups.all().exists():
            count_has_group += 1
        if u.validate:
            count_validate += 1
    can_begin = (count_has_group == count_validate)     # we can start the simulation

    if has_begun:
        instance = Worker.objects.get(dateW=last_week)
    else:
        instance = None
    if request.method == 'POST':
        f = WorkersForm(request.POST, instance=instance)  # changes group
        if f.is_valid():
            f.save()
            messages.success(request, 'Worker info changed')
            return redirect('/controltower')

    else:
        f = WorkersForm(instance=instance)

    context = {
        'all_users': all_users,
        'can_begin': can_begin,
        'has_begun': has_begun,
        'f': f,
        'first_week': first_week,
    }
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

    good = Goods.objects.get(idG__exact=idg)
    if request.method == 'POST':
        if good.idG in ['F1', 'F2']:
            f = GoodChangeForm(request.POST, instance=good)  # changes good
        else:
            f = GoodChangeForm_1(request.POST, instance=good)
        if f.is_valid():
            f.save()
            messages.success(request, 'Info changed successfully')
            return redirect('/controltower/valid')

    else:
        if good.idG in ['F1', 'F2']:
            f = GoodChangeForm(instance=good)  # changes good
        else:
            f = GoodChangeForm_1(instance=good)

    return render(request, 'controltower/editgood.html', {'form': f, 'idG': idg})


@user_passes_test(lambda u: u.is_superuser)
def valid(request):
    has_begun = Week.objects.all().exists()
    all_users = User.objects.all()

    if has_begun:
        return redirect('/controltower/new_week')
    else:
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
def costs(request):

    weeks = Week.objects.all().order_by('week')
    last_week = weeks.last()
    all_infos = InfoUser.objects.filter(date=last_week)
    CostFormSet = modelformset_factory(InfoUser, fields=['fixed_cost', ], extra=0)

    if request.method == 'POST':
        f = CostFormSet(request.POST, queryset=all_infos)  # change costs
        if f.is_valid():
            f.save()
            messages.success(request, 'Costs changed successfully')
            return redirect('/controltower')
    f = CostFormSet(queryset=all_infos)
    return render(request, 'controltower/costs.html', context={'f': f})


@user_passes_test(lambda u: u.is_superuser)
def begin_simulation(request):

    week_1 = Week(week=1)
    week_1.save()

    # create all infos
    for user in User.objects.all():
        user.validate = False
        user.save()
        info = InfoUser(user=user, date=week_1)
        info.save()

    # create worker
    worker = Worker(dateW=week_1)
    worker.save()

    warehouses = User.objects.filter(groups__name__exact='Warehouses')
    logistics = User.objects.filter(groups__name__exact='Logistics')
    distributors = User.objects.filter(groups__name__exact='Distributors')


    # create all paths
    if warehouses.exists() and logistics.exists() and distributors.exists():
        for warehouse in warehouses:
            for distributor in distributors:
                for logistic in logistics:
                    id = warehouse.codename + distributor.codename + logistic.codename + str(week_1.week)
                    path = Path(idP=id,
                                sellerP=warehouse,
                                buyerP=distributor,
                                logicP=logistic,
                                dateP=week_1)
                    path.save()
    return render(request, 'controltower/begin_simulation.html')


@user_passes_test(lambda u: u.is_superuser)
def new_week(request):

    def change_partial_stock(quan, idU, goods):
        while quan > 0:
            non_empty_stocks = Stock.objects.filter(idU=idU, goods=goods).\
                exclude(partialS=0).order_by('dateS')
            if non_empty_stocks.exists():
                first_stock = non_empty_stocks.first()
                if quan < first_stock.partialS:
                    first_stock.partialS -= quan
                    quan = 0
                else:
                    quan -= first_stock.partialS
                    first_stock.partialS = 0
                first_stock.save()
            else:
                quan = 0 # should never happen

    weeks = Week.objects.all().order_by('week')
    last_week = weeks.last()
    new_week = Week(week=last_week.week + 1)
    new_week.save()
    v_transactions = Transaction.objects.filter(dateT=last_week, verifiedT=True)

    # create new worker
    worker = Worker.objects.get(dateW=last_week)
    new_worker = Worker(dateW=new_week, eff=worker.eff, sal=worker.sal)
    new_worker.save()

    # create new info_user
    infos = InfoUser.objects.filter(date=last_week)
    for info in infos:
        new_info = InfoUser(user=info.user, funds=info.funds, numT=info.numT, fixed_cost=info.fixed_cost, date=new_week)
        new_info.save()

    # create new stocks
    stocks = Stock.objects.filter(dateS=last_week)
    for stock in stocks:
        id = stock.idU.codename + stock.goods.idG + str(new_week.week)
        new_stock_buyer = Stock(idS=id, idU=stock.idU, goods=stock.goods, dateS=new_week, quanS=stock.quanS)
        new_stock_buyer.save()

    # create new paths
    paths = Path.objects.filter(dateP=last_week)
    for path in paths:
        id = path.sellerP.codename + path.buyerP.codename + path.logicP.codename + str(new_week.week)
        new_path = Path(idP=id, sellerP=path.sellerP, buyerP=path.buyerP, logicP=path.logicP,
                        priceP=path.priceP, chosenP=path.chosenP, dateP=new_week)
        new_path.save()

    # goods transformations
    suppliers_a = User.objects.filter(groups__name__exact='Suppliers_A')
    suppliers_b = User.objects.filter(groups__name__exact='Suppliers_B')
    factories = User.objects.filter(groups__name__exact='Factories')
    for user in suppliers_a:
        stock_raw_1 = Stock.objects.get(goods__idG__exact='R1', idU__exact=user, dateS=new_week)
        stock_raw_3 = Stock.objects.get(goods__idG__exact='R3', idU__exact=user, dateS=new_week)
        stock_product_1 = Stock.objects.get(goods__idG__exact='P1', idU__exact=user, dateS=new_week)
        stock_product_3 = Stock.objects.get(goods__idG__exact='P3', idU__exact=user, dateS=new_week)
        worker = Worker.objects.get(dateW=new_week)
        info = InfoUser.objects.get(user=user, date=new_week)
        capa = user.maxT + info.numT * worker.eff

        # good 1
        c = stock_raw_1.goods.coefG
        if stock_raw_1.quanS * c > capa:
            quan = capa * c
            stock_product_1.quanS = stock_product_1.quanS + capa
            stock_raw_1.quanS = stock_raw_1.quanS - capa * c
            stock_product_1.partialS += capa

        else:
            quan = (stock_raw_1.quanS // c) * c
            stock_product_1.quanS = stock_product_1.quanS + stock_raw_1.quanS // c
            stock_raw_1.quanS = stock_raw_1.quanS - quan
            stock_product_1.partialS += stock_raw_1.quanS // c

        stock_raw_1.save()
        stock_product_1.save()
        change_partial_stock(quan, user, stock_raw_1.goods)

        # good 3
        c = stock_raw_3.goods.coefG
        if stock_raw_3.quanS * c > capa:
            quan = capa * c
            stock_product_3.quanS = stock_product_3.quanS + capa
            stock_raw_3.quanS = stock_raw_3.quanS - capa * c
            stock_product_3.partialS += capa

        else:
            quan = (stock_raw_3.quanS // c) * c
            stock_product_3.quanS = stock_product_3.quanS + stock_raw_3.quanS // c
            stock_raw_3.quanS = stock_raw_3.quanS - quan
            stock_product_3.partialS += stock_raw_3.quanS // c
        stock_raw_3.save()
        stock_product_3.save()
        change_partial_stock(quan, user, stock_raw_3.goods)

    for user in suppliers_b:
        stock_raw_2 = Stock.objects.get(goods__idG__exact='R2', idU__exact=user, dateS=new_week)
        stock_raw_4 = Stock.objects.get(goods__idG__exact='R4', idU__exact=user, dateS=new_week)
        stock_product_2 = Stock.objects.get(goods__idG__exact='P2', idU__exact=user, dateS=new_week)
        stock_product_4 = Stock.objects.get(goods__idG__exact='P4', idU__exact=user, dateS=new_week)
        worker = Worker.objects.get(dateW=new_week)
        info = InfoUser.objects.get(user=user, date=new_week)
        capa = user.maxT + info.numT * worker.eff

        # good 2
        c = stock_raw_2.goods.coefG
        if stock_raw_2.quanS * c > capa:
            quan = capa * c
            stock_product_2.quanS = stock_product_2.quanS + capa
            stock_raw_2.quanS = stock_raw_2.quanS - capa * c
            stock_product_2.partialS += capa
        else:
            quan = (stock_raw_2.quanS // c) * c
            stock_product_2.quanS = stock_product_2.quanS + stock_raw_2.quanS // c
            stock_raw_2.quanS = stock_raw_2.quanS - quan
            stock_product_2.partialS += stock_raw_2.quanS // c
        stock_raw_2.save()
        stock_product_2.save()
        change_partial_stock(quan, user, stock_raw_2.goods)

        # good 4
        c = stock_raw_4.goods.coefG
        if stock_raw_4.quanS * c > capa:
            quan = capa * c
            stock_product_4.quanS = stock_product_4.quanS + capa
            stock_raw_4.quanS = stock_raw_4.quanS - capa * c
            stock_product_4.partialS += capa
        else:
            quan = ( stock_raw_4.quanS // c) * c
            stock_product_4.quanS = stock_product_4.quanS + stock_raw_4.quanS // c
            stock_raw_4.quanS = stock_raw_4.quanS - quan
            stock_product_4.partialS += stock_raw_4.quanS // c
        stock_raw_4.save()
        stock_product_4.save()
        change_partial_stock(quan, user, stock_raw_4.goods)

    for user in factories:
        stock_product_1 = Stock.objects.get(goods__idG__exact='P1', idU__exact=user, dateS=new_week)
        stock_product_2 = Stock.objects.get(goods__idG__exact='P2', idU__exact=user, dateS=new_week)
        stock_product_3 = Stock.objects.get(goods__idG__exact='P3', idU__exact=user, dateS=new_week)
        stock_product_4 = Stock.objects.get(goods__idG__exact='P4', idU__exact=user, dateS=new_week)
        stock_final_1 = Stock.objects.get(goods__idG__exact='F1', idU__exact=user, dateS=new_week)
        stock_final_2 = Stock.objects.get(goods__idG__exact='F2', idU__exact=user, dateS=new_week)
        worker = Worker.objects.get(dateW=new_week)
        info = InfoUser.objects.get(user=user, date=new_week)
        capa = user.maxT + info.numT * worker.eff

        # product 1
        c1 = stock_product_1.goods.coefG
        c2 = stock_product_2.goods.coefG
        if stock_product_1.quanS * c1 > capa and stock_product_2.quanS * c2 > capa:
            quan = capa
            quan1 = capa * c1
            quan2 = capa * c2
            stock_final_1.quanS = stock_final_1.quanS + capa
            stock_product_1.quanS = stock_product_1.quanS - capa * c1
            stock_product_2.quanS = stock_product_2.quanS - capa * c2
        else:
            quan = min(stock_product_1.quanS // c1, stock_product_2.quanS // c2)
            quan1 = quan * c1
            quan2 = quan * c2
            stock_final_1.quanS = stock_final_1.quanS + quan
            stock_product_1.quanS = stock_product_1.quanS - quan * c1
            stock_product_2.quanS = stock_product_2.quanS - quan * c2
        stock_final_1.partialS += quan
        stock_final_1.save()
        stock_product_1.save()
        stock_product_2.save()
        change_partial_stock(quan1, user, stock_product_1.goods)
        change_partial_stock(quan2, user, stock_product_2.goods)

        # product 2
        c1 = stock_product_3.goods.coefG
        c2 = stock_product_4.goods.coefG
        if stock_product_3.quanS * c1 > capa and stock_product_4.quanS * c2 > capa:
            quan = capa
            quan1 = capa * c1
            quan2 = capa * c2
            stock_final_2.quanS = stock_final_2.quanS + capa
            stock_product_3.quanS = stock_product_3.quanS - capa
            stock_product_4.quanS = stock_product_4.quanS - capa
        else:
            quan = min(stock_product_3.quanS // c1, stock_product_4.quanS // c2)
            quan1 = quan * c1
            quan2 = quan * c2
            stock_final_2.quanS = stock_final_2.quanS + quan
            stock_product_3.quanS = stock_product_3.quanS - quan * c1
            stock_product_4.quanS = stock_product_4.quanS - quan * c2
        stock_final_2.partialS += quan
        stock_final_2.save()
        stock_product_3.save()
        stock_product_4.save()
        change_partial_stock(quan1, user, stock_product_3.goods)
        change_partial_stock(quan2, user, stock_product_4.goods)

    # all changed linked to transactions
    for tran in v_transactions:

        if tran.buyerT.codename != 'A':
            # new stock for buyer
            stock_buyer = Stock.objects.get(idU=tran.buyerT, goods=tran.goods, dateS=new_week)
            stock_buyer.quanS += tran.quanT
            stock_buyer.partialS += tran.quanT
            stock_buyer.save()

            # new funds for buyer
            info = InfoUser.objects.get(user=tran.buyerT, date=new_week)
            new_funds = info.funds - tran.quanT * tran.priceT
            info.funds = new_funds
            info.save()

        if tran.sellerT.codename != 'A':
            # new stock for seller
            stock_seller = Stock.objects.get(idU=tran.sellerT, goods=tran.goods, dateS=new_week)
            stock_seller.quanS -= tran.quanT
            stock_seller.save()
            quan = tran.quanT
            change_partial_stock(quan, tran.sellerT, tran.goods)

            # new funds for seller
            info = InfoUser.objects.get(user=tran.sellerT, date=new_week)
            new_funds = info.funds + tran.quanT * tran.priceT
            info.funds = new_funds
            info.save()

    # logistics
    paths = Path.objects.all()
    for path in paths:
        if path.chosenP:
            all_tran = Transaction.objects.filter(sellerT=path.sellerP, buyerT=path.buyerP,
                                                  dateT=last_week, verifiedT=True)
            info_logic = InfoUser.objects.get(user=path.logicP, date=new_week)
            info_seller = InfoUser.objects.get(user=path.sellerP, date=new_week)
            for tran in all_tran:
                info_logic.funds += tran.quanT * path.priceP
                info_seller.funds -= tran.quanT * path.priceP
                info_logic.save()
                info_seller.save()

    # fixed costs and salaries
    for user in User.objects.all():
        info = InfoUser.objects.get(user=user, date=new_week)
        new_funds = info.funds - info.fixed_cost
        new = new_funds - info.numT * Worker.objects.get(dateW=new_week).sal
        info.funds = new
        info.save()
        user.validate = False
        user.save()

    # expiration
    goods = Goods.objects.all()
    for good in goods:
        expiration = new_week.week - good.durG - 1
        if Week.objects.filter(week=expiration).exists():
            expiration_week = Week.objects.get(week=expiration)
            stocks = Stock.objects.filter(goods=good, dateS=expiration_week)
            for stock in stocks:
                total_stock = Stock.objects.get(goods=good, idU=stock.idU, dateS=new_week)
                total_stock.quanS -= stock.partialS
                stock.partialS = 0
                total_stock.save()
                stock.save()

    return redirect('/')


def kpi(request):

    users = User.objects.exclude(codename='A')
    last_week = Week.objects.all().last()
    week = Week.objects.get(week=last_week.week - 1)
    if Week.objects.filter(week=last_week.week - 2).exists():
        previous_week = Week.objects.get(week=last_week.week - 2)
    else:
        previous_week = None
    paths = Path.objects.all()
    worker = Worker.objects.get(dateW=week)
    dict_kpi = {}

    for user in users:

        # KPI1
        if user.groups.first().name != 'Logistics':
            sum_order = Order.objects.filter(sellerO=user, dateO=previous_week).aggregate(Sum('quanO'))
            sum_tran = Transaction.objects.filter(sellerT=user, dateT=week, verifiedT=True).aggregate(Sum('quanT'))
            if sum_order['quanO__sum'] == 0:
                dict_kpi.update({user.codename + 'KPI1': '#DIV0'})
            elif sum_order['quanO__sum'] is None or sum_tran['quanT__sum'] is None:
                dict_kpi.update({user.codename + 'KPI1': 'NONE'})
            else:
                dict_kpi.update({user.codename + 'KPI1': sum_tran['quanT__sum'] / sum_order['quanO__sum']})
        else:
            dict_kpi.update({user.codename + 'KPI1': 'L'})

        # KPI2
        if user.groups.first().name != 'Logistics':
            sum_tran = Transaction.objects.filter(sellerT=user, dateT=week, verifiedT=True).aggregate(Sum('quanT'))
            stock = Stock.objects.filter(idU=user, dateS=week).aggregate(Sum('quanS'))
            if stock['quanS__sum'] == 0:
                dict_kpi.update({user.codename + 'KPI2': '#DIV0'})
            elif sum_tran['quanT__sum'] is None or stock['quanS__sum'] is None:
                dict_kpi.update({user.codename + 'KPI2': 'NONE'})
            else:
                dict_kpi.update({user.codename + 'KPI2': sum_tran['quanT__sum'] / stock['quanS__sum']})
        else:
            dict_kpi.update({user.codename + 'KPI2': 'L'})

        # KPI3
        info_user = InfoUser.objects.get(user=user, date=week)
        sum_costs = info_user.fixed_cost
        sum_costs += info_user.numT * worker.sal
        sum_profits = 0
        if user.groups.first().name != 'Logistics':
            tran_buy = Transaction.objects.filter(buyerT=user, dateT=week, verifiedT=True)
            for tran in tran_buy:
                sum_costs += tran.quanT * tran.priceT

            tran_sale = Transaction.objects.filter(sellerT=user, dateT=week, verifiedT=True)
            for tran in tran_sale:
                sum_profits += tran.quanT * tran.priceT
        else:
            for path in paths:
                if path.chosenP:
                    all_tran = Transaction.objects.filter(sellerT=path.sellerP, buyerT=path.buyerP,
                                                          dateT=week, verifiedT=True)
                    for tran in all_tran:
                        sum_profits += tran.quanT * path.priceP
        if user.groups.first().name == 'Warehouses':
            user_paths = Path.objects.filter(sellerP=user)
            for path in user_paths:
                if path.chosenP:
                    all_tran = Transaction.objects.filter(sellerT=path.sellerP, buyerT=path.buyerP,
                                                          dateT=week, verifiedT=True)
                    for tran in all_tran:
                        sum_costs += tran.quanT * path.priceP
        if sum_costs == 0:
            dict_kpi.update({user.codename + 'KPI3': '#DIV0'})
        else:
            dict_kpi.update({user.codename + 'KPI3': sum_profits / sum_costs})

    context = {
        'users': users,
        'week': week,
        'dict_kpi': dict_kpi,
    }
    return render(request, 'controltower/kpi.html', context=context)

@user_passes_test(lambda u: u.is_superuser)
def confirmation(request):
    return render(request, 'controltower/confirmation.html')

@user_passes_test(lambda u: u.is_superuser)
def delete(request):
    User.objects.all().delete()
    Group.objects.all().delete()
    Week.objects.all().delete()
    InfoUser.objects.all().delete()
    Goods.objects.all().delete()
    Stock.objects.all().delete()
    Order.objects.all().delete()
    Transaction.objects.all().delete()
    Worker.objects.all().delete()
    Path.objects.all().delete()

    return redirect('/')