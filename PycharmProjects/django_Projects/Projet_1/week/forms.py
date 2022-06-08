from django.contrib.auth import get_user_model
from django.forms import ModelForm, BaseModelFormSet
from django import forms
from django.core.exceptions import ValidationError
from data.models import CustomUser, Stock, Order, Week
from django.contrib.auth.forms import UserChangeForm

User = get_user_model()


class ChangeUser_1(ModelForm):
    password = None

    class Meta:
        model = User
        fields = ('funds', 'validate', 'maxT')


class ChangeUser(ModelForm):
    password = None

    class Meta:
        model = User
        fields = ('validate',)


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


class BaseSalesLFormset(BaseModelFormSet):

    def clean(self):
        cleaned_data = super(BaseSalesLFormset, self).clean()
        if any(self.errors):
            return

        total = 0
        for form in self.forms:
            tran = form.instance
            logic = tran.transporter
            total += tran.quanT
        if total > logic.maxT:
            raise ValidationError('The transactions are greater than the max capacity')

        return cleaned_data


class WorkerForm(UserChangeForm):
    password = None

    class Meta:
        model = CustomUser
        fields = ('numT', )
