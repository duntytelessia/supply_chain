from django.contrib.auth import get_user_model
from django.forms import ModelForm, BaseModelFormSet, BaseFormSet
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserChangeForm
from data.models import CustomUser, Stock, Order, Week, Transaction, Worker, InfoUser, Goods

User = get_user_model()


class ChangeUser_1(ModelForm):
    password = None

    class Meta:
        model = User
        fields = ('validate', 'maxT')


class ChangeUser(ModelForm):
    password = None

    class Meta:
        model = User
        fields = ('validate',)


class ChangeInfoUser(ModelForm):

    class Meta:
        model = InfoUser
        fields = ('funds',)


class LogicForm(forms.Form):

    chose = forms.ModelChoiceField(User.objects.filter(groups__name__exact='Logistics'), required=True, label='')


class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


class BaseSalesFormset(BaseModelFormSet):

    def clean(self):
        cleaned_data = super(BaseSalesFormset, self).clean()
        if any(self.errors):
            return

        by_goods = dict()
        by_buyer = dict()
        for form in self.forms:
            tran = form.instance
            if tran.goods in by_goods.keys():
                by_goods[tran.goods].append(tran)
            else:
                by_goods.update({tran.goods: [tran, ]})

            if tran.buyerT in by_buyer.keys():
                by_buyer[tran.buyerT].append(tran)
            else:
                by_buyer.update({tran.buyerT: [tran, ]})

        # stock verification
        for good in by_goods.keys():
            total = 0
            for tran in by_goods[good]:
                stock = Stock.objects.get(idU=tran.sellerT, goods=good, dateS=tran.dateT)
                total += tran.quanT
            if total > stock.quanS:
                raise ValidationError(str(good.nameG) + ': total of transactions is greater than stock')

        for good in by_goods.keys():
            for tran in by_goods[good]:
                goo = Goods.objects.get(nameG=tran.goods)
            if tran.priceT < goo.minG:
                raise ValidationError(str(tran.buyerT.codename) + ' ' + str(tran.goods.nameG) +
                                      ': Transaction Price is lower than min price.')
            if tran.priceT > goo.maxG:
                raise ValidationError(str(tran.buyerT.codename) + ' ' + str(tran.goods.nameG) +
                                      ': Transaction Price is higher than max price.')

        # order verification:
        for good in by_goods.keys():
            for buyer in by_buyer.keys():
                total = 0
                for tran in by_goods[good]:
                    last_week = Week.objects.get(week=tran.dateT.week - 1)
                    order = Order.objects.get(sellerO=tran.sellerT, buyerO=buyer, goods=good, dateO=last_week)
                    if tran in by_buyer[buyer]:
                        total += tran.quanT
                if total > order.quanO:
                    raise ValidationError(str(good.nameG) + ' ' +
                                          str(buyer.codename) + ': total of transactions in greater than order')

        return cleaned_data


class BaseSalesAFormset(BaseModelFormSet):

    def clean(self):
        cleaned_data = super(BaseSalesAFormset, self).clean()
        if any(self.errors):
            return

        for form in self.forms:
            tran = form.instance
            last_week = Week.objects.get(week=tran.dateT.week - 1)
            order = Order.objects.get(sellerO=tran.sellerT, buyerO=tran.buyerT, goods=tran.goods, dateO=last_week)
            if tran.quanT > order.quanO:
                raise ValidationError(str(tran.buyerT.codename) + ' ' + str(tran.goods.nameG) +
                                      ': Transaction is greater than order')

            for form in self.forms:
                tran = form.instance
                goo = Goods.objects.get(nameG=tran.goods)
                if tran.priceT < goo.minG:
                    raise ValidationError(str(tran.buyerT.codename) + ' ' + str(tran.goods.nameG) +
                                          ': Transaction Price is lower than min price.')
                if tran.priceT > goo.maxG:
                    raise ValidationError(str(tran.buyerT.codename) + ' ' + str(tran.goods.nameG) +
                                          ': Transaction Price is higher than max price.')





class BaseSalesLFormset(BaseModelFormSet):

    def __init__(self, user, week, *args, **kwargs):
        self.user = user
        self.week = week
        super(BaseSalesLFormset, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(BaseSalesLFormset, self).clean()
        if any(self.errors):
            return

        worker = Worker.objects.get(dateW=self.week)
        info = InfoUser.objects.get(user=self.user, date=self.week)
        capa = self.user.maxT + info.numT * worker.eff
        total = 0
        by_gu = dict()
        for form in self.forms:
            tran = form.instance
            total += tran.quanT

            id_o = tran.idT[:-1] + str(tran.dateT.week - 1)
            id_s = tran.sellerT.codename + tran.goods.idG + str(self.week.week)
            order = Order.objects.get(idO__exact=id_o)
            stock = Stock.objects.get(idS__exact=id_s)
            if tran.quanT > order.quanO:
                raise ValidationError(str(tran.sellerT) + ' to ' + str(tran.buyerT) + ': '
                                      + str(tran.goods) + '     Transaction is greater than order')
            if tran.goods.idG + tran.sellerT.codename in by_gu.keys():
                by_gu[tran.goods.idG + tran.sellerT.codename].append(tran)
            else:
                by_gu.update({tran.goods.idG + tran.sellerT.codename: [tran, ]})

        for code in by_gu.keys():
            total_g = 0
            for tran in by_gu[code]:
                stock = Stock.objects.get(idU=tran.sellerT, goods=tran.goods, dateS=tran.dateT)
                total_g += tran.quanT
            if total_g > stock.quanS:
                raise ValidationError(code + ': total of transactions is greater than stock')

        if total > capa:
            raise ValidationError('The transactions are greater than the max capacity')

        return cleaned_data


class WorkerForm(ModelForm):

    class Meta:
        model = InfoUser
        fields = ('numT', )
