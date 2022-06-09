from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from controltower.forms import GroupChangeForm, GoodChangeForm, WorkersForm
from data.models import Goods, Week, Order, Transaction, Stock, Worker, Path
from django.forms import modelformset_factory
from controltower.forms import *


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

    if request.method == 'POST':
        f = WorkersForm(request.POST, instance=Worker.objects.get(id__exact='0'))  # changes group
        if f.is_valid():
            f.save()
            messages.success(request, 'Worker info changed')
            return redirect('/controltower')

    else:
        f = WorkersForm(instance=Worker.objects.get(id__exact='0'))

    tt = Transaction.objects.all()
    for t in tt:
        tid = t.idT
        tseller = t.sellerT
        tbuyer = t.buyerT
        tgoods = t.goods
        tquan = t.quanT
        tdate = t.dateT
        tprice = t.priceT
        tverified = t.verifiedT

    oo = Order.objects.all()

    context = {
        'all_users': all_users,
        'can_begin': can_begin,
        'has_begun': has_begun,
        'f': f,
        'tt': tt,
        'tid': tid,
        'tseller': tseller,
        'tbuyer': tbuyer,
        'tgoods': tgoods,
        'tquan': tquan,
        'tdate': tdate,
        'tprice': tprice,
        'tverified': tverified,
        'oo' : oo,

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

    all_users = User.objects.all()
    CostFormSet = modelformset_factory(User, fields=['fixed_cost', ], extra=0)

    if request.method == 'POST':
        f = CostFormSet(request.POST, queryset=all_users)  # change costs
        if f.is_valid():
            f.save()
            messages.success(request, 'Costs changed successfully')
            return redirect('/controltower')
    f = CostFormSet(queryset=all_users)
    return render(request, 'controltower/costs.html', context={'f': f})


@user_passes_test(lambda u: u.is_superuser)
def begin_simulation(request):

    # unvalidate all
    for user in User.objects.all():
        user.validate = False
        user.save()


    # create all paths
    warehouses = User.objects.filter(groups__name__exact='Warehouses')
    logistics = User.objects.filter(groups__name__exact='Logistics')
    distributors = User.objects.filter(groups__name__exact='Distributors')
    if warehouses.exists() and logistics.exists() and distributors.exists():
        for warehouse in warehouses:
            for distributor in distributors:
                for logistic in logistics:
                    id = warehouse.codename + distributor.codename + logistic.codename
                    path = Path(idP=id,
                                sellerP=warehouse,
                                buyerP=distributor,
                                logicP=logistic)
                    path.save()

    week_1 = Week(week=1)
    week_1.save()
    return render(request, 'controltower/begin_simulation.html')


@user_passes_test(lambda u: u.is_superuser)
def new_week(request):
    weeks = Week.objects.all().order_by('week')
    last_week = weeks.last()
    new_week = Week(week=last_week.week + 1)
    new_week.save()
    v_transactions = Transaction.objects.filter(dateT=last_week, verifiedT=True)

    # create new stocks
    stocks = Stock.objects.filter(dateS=last_week)
    for stock in stocks:
        id = stock.idU.codename + stock.goods.idG + str(new_week.week)
        new_stock_buyer = Stock(idS=id, idU=stock.idU, goods=stock.goods, dateS=new_week, quanS=stock.quanS)
        new_stock_buyer.save()

    # all changed linked to transactions
    for tran in v_transactions:

        if tran.buyerT.codename != 'A':
            # new stock for buyer
            stock_buyer = Stock.objects.get(idU=tran.buyerT, goods=tran.goods, dateS=last_week)
            new_quanS = stock_buyer.quanS + tran.quanT
            id = stock_buyer.idU.codename + stock_buyer.goods.idG + str(new_week.week)
            new_stock_buyer = Stock(idS=id, idU=stock_buyer.idU, goods=stock_buyer.goods, dateS=new_week, quanS=new_quanS)
            new_stock_buyer.save()

            # new funds for buyer
            new_funds = tran.buyerT.funds - tran.quanT * tran.priceT
            tran.buyerT.funds = new_funds
            tran.buyerT.save()

        if tran.sellerT.codename != 'A':
            # new stock for seller
            stock_seller = Stock.objects.get(idU=tran.sellerT, goods=tran.goods, dateS=last_week)
            new_quanS = stock_seller.quanS - tran.quanT
            id = stock_seller.idU.codename + stock_seller.goods.idG + str(new_week.week)
            new_stock_seller = Stock(idS=id, idU=stock_seller.idU, goods=stock_seller.goods, dateS=new_week, quanS=new_quanS)
            new_stock_seller.save()

            # new funds for seller
            new_funds = tran.sellerT.funds + tran.quanT * tran.priceT
            tran.sellerT.funds = new_funds
            tran.sellerT.save()

    # goods transformations
    suppliers_a = User.objects.filter(groups__name__exact='Suppliers_A')
    suppliers_b = User.objects.filter(groups__name__exact='Suppliers_B')
    factories = User.objects.filter(groups__name__exact='Factories')
    for user in suppliers_a:
        stock_raw_1 = Stock.objects.get(goods__idG__exact='R1', idU__exact=user, dateS=new_week)
        stock_raw_3 = Stock.objects.get(goods__idG__exact='R3', idU__exact=user, dateS=new_week)
        stock_product_1 = Stock.objects.get(goods__idG__exact='P1', idU__exact=user, dateS=new_week)
        stock_product_3 = Stock.objects.get(goods__idG__exact='P3', idU__exact=user, dateS=new_week)
        worker = Worker.objects.get(id__exact='0')
        capa = user.maxT + user.numT * worker.eff

        # good 1
        c = stock_raw_1.goods.coefG
        if stock_raw_1.quanS * c > capa:
            stock_product_1.quanS = stock_product_1.quanS + capa
            stock_raw_1.quanS = stock_raw_1.quanS - capa * c
        else:
            stock_product_1.quanS = stock_product_1.quanS + stock_raw_1.quanS // c
            stock_raw_1.quanS = stock_raw_1.quanS % c
        stock_raw_1.save()
        stock_product_1.save()

        # good 3
        c = stock_raw_3.goods.coefG
        if stock_raw_3.quanS * c > capa:
            stock_product_3.quanS = stock_product_3.quanS + capa
            stock_raw_3.quanS = stock_raw_3.quanS - capa * c
        else:
            stock_product_3.quanS = stock_product_3.quanS + stock_raw_3.quanS // c
            stock_raw_3.quanS = stock_raw_3.quanS % c
        stock_raw_3.save()
        stock_product_3.save()

    for user in suppliers_b:
        stock_raw_2 = Stock.objects.get(goods__idG__exact='R2', idU__exact=user, dateS=new_week)
        stock_raw_4 = Stock.objects.get(goods__idG__exact='R4', idU__exact=user, dateS=new_week)
        stock_product_2 = Stock.objects.get(goods__idG__exact='P2', idU__exact=user, dateS=new_week)
        stock_product_4 = Stock.objects.get(goods__idG__exact='P4', idU__exact=user, dateS=new_week)
        worker = Worker.objects.get(id__exact='0')
        capa = user.maxT + user.numT * worker.eff

        # good 2
        c = stock_raw_2.goods.coefG
        if stock_raw_2.quanS * c > capa:
            stock_product_2.quanS = stock_product_2.quanS + capa
            stock_raw_2.quanS = stock_raw_2.quanS - capa * c
        else:
            stock_product_2.quanS = stock_product_2.quanS + stock_raw_2.quanS // c
            stock_raw_2.quanS = stock_raw_2.quanS % c
        stock_raw_2.save()
        stock_product_2.save()

        # good 4
        c = stock_raw_4.goods.coefG
        if stock_raw_4.quanS * c > capa:
            stock_product_4.quanS = stock_product_4.quanS + capa
            stock_raw_4.quanS = stock_raw_4.quanS - capa * c
        else:
            stock_product_4.quanS = stock_product_4.quanS + stock_raw_4.quanS // c
            stock_raw_4.quanS = stock_raw_4.quanS % c
        stock_raw_4.save()
        stock_product_4.save()

    for user in factories:
        stock_product_1 = Stock.objects.get(goods__idG__exact='P1', idU__exact=user, dateS=new_week)
        stock_product_2 = Stock.objects.get(goods__idG__exact='P2', idU__exact=user, dateS=new_week)
        stock_product_3 = Stock.objects.get(goods__idG__exact='P3', idU__exact=user, dateS=new_week)
        stock_product_4 = Stock.objects.get(goods__idG__exact='P4', idU__exact=user, dateS=new_week)
        stock_final_1 = Stock.objects.get(goods__idG__exact='F1', idU__exact=user, dateS=new_week)
        stock_final_2 = Stock.objects.get(goods__idG__exact='F2', idU__exact=user, dateS=new_week)
        worker = Worker.objects.get(id__exact='0')
        capa = user.maxT + user.numT * worker.eff

        # product 1
        c1 = stock_product_1.goods.coefG
        c2 = stock_product_2.goods.coefG
        if stock_product_1.quanS * c1 > capa and stock_product_2.quanS * c2 > capa:
            stock_final_1.quanS = stock_final_1.quanS + capa
            stock_product_1.quanS = stock_product_1.quanS - capa * c1
            stock_product_2.quanS = stock_product_2.quanS - capa * c2
        else:
            quan = min(stock_product_1.quanS // c1, stock_product_2.quanS // c2)
            stock_final_1.quanS = stock_final_1.quanS + quan
            stock_product_1.quanS = stock_product_1.quanS - quan * c1
            stock_product_2.quanS = stock_product_2.quanS - quan * c2
        stock_final_1.save()
        stock_product_1.save()
        stock_product_2.save()

        # product 2
        c1 = stock_product_3.goods.coefG
        c2 = stock_product_4.goods.coefG
        if stock_product_3.quanS * c1 > capa and stock_product_4.quanS * c2 > capa:
            stock_final_2.quanS = stock_final_2.quanS + capa
            stock_product_3.quanS = stock_product_3.quanS - capa
            stock_product_4.quanS = stock_product_4.quanS - capa
        else:
            quan = min(stock_product_3.quanS // c1, stock_product_4.quanS // c2)
            stock_final_2.quanS = stock_final_2.quanS + quan
            stock_product_3.quanS = stock_product_3.quanS - quan * c1
            stock_product_4.quanS = stock_product_4.quanS - quan * c2
        stock_final_2.save()
        stock_product_3.save()
        stock_product_4.save()

    for user in User.objects.all():
        new_funds = user.funds - user.fixed_cost
        user.funds = new_funds
        user.validate = False
        new = user.funds - user.numT * Worker.objects.get(id__exact='0').sal
        user.funds = new
        user.save()


    return redirect('/')
