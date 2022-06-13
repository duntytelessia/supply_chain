from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


#Utilisateur
class CustomUser(AbstractUser):
    validate = models.BooleanField(default=False)
    codename = models.CharField(max_length=10, default='A')
    maxT = models.FloatField(default=1000)

    def __str__(self):
        return str(self.codename)


class Week(models.Model):
    week = models.PositiveIntegerField()

    def __str__(self):
        return str(self.week)


class InfoUser(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    date = models.ForeignKey(Week, on_delete=models.CASCADE, default=1)
    funds = models.FloatField(default=0)
    numT = models.IntegerField(default=0)
    fixed_cost = models.FloatField(default=1000)


# Marchandise
class Goods(models.Model):
    idG = models.CharField(max_length=200, primary_key=True)
    nameG = models.CharField(max_length=200)
    durG = models.PositiveIntegerField()  # keep
    coefG = models.FloatField(default=1)  # it needs n good to transform in 1 other good.

    def __str__(self):
        return self.nameG

    class Meta:
        verbose_name_plural = "Goods"


class Stock(models.Model):
    idS = models.CharField(max_length=200, primary_key=True)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, default=2)
    idU = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=2)
    quanS = models.FloatField(default=0)
    partialS = models.FloatField(default=0)
    dateS = models.ForeignKey(Week, on_delete=models.CASCADE, default=1)


#Commande
class Order(models.Model):
    idO = models.CharField(max_length=200, primary_key=True)
    sellerO = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='order_seller', default=2)
    buyerO = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='order_buyer', default=2)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, default=2)
    quanO = models.FloatField(default=0)
    dateO = models.ForeignKey(Week, on_delete=models.CASCADE, default=1)


class Transaction(models.Model):
    idT = models.CharField(max_length=200, primary_key=True)
    sellerT = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tran_seller', default=2)
    buyerT = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tran_buyer', default=2)
    quanT = models.FloatField(default=0)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, default=2)
    dateT = models.ForeignKey(Week, on_delete=models.CASCADE, default=1)
    priceT = models.FloatField(default=0)
    verifiedT = models.BooleanField(default=False)


class Worker(models.Model):
    dateW = models.ForeignKey(Week, on_delete=models.CASCADE, default=1)
    eff = models.FloatField(default=100)  # keep
    sal = models.FloatField(default=100)  # keep


class Path(models.Model):
    idP = models.CharField(max_length=200, primary_key=True)
    sellerP = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='path_seller', default=2)
    buyerP = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='path_buyer', default=2)
    logicP = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='path_logic', default=1)
    priceP = models.FloatField(default=0)  # keep
    chosenP = models.BooleanField(default=False)
    dateP = models.ForeignKey(Week, on_delete=models.CASCADE, default=1)

