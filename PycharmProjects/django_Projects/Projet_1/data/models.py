from django.db import models
from django.contrib.auth.models import AbstractUser


#Utilisateur
class CustomUser(AbstractUser):
    validate = models.BooleanField(default=False)
    codename = models.CharField(max_length=10, default='A')


class Week(models.Model):
    week = models.PositiveIntegerField()

    def __str__(self):
        return str(self.week)


#Marchandise
class Goods(models.Model):
    idG = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=2)
    nameG = models.CharField(max_length=200)
    durG = models.DurationField()


class Stock(models.Model):
    idS = models.BigAutoField(primary_key=True)
    idG = models.ForeignKey(Goods, on_delete=models.CASCADE)
    idU = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=2)
    quanS = models.FloatField()
    dateS = models.DateField()


#Commande
class Order(models.Model):
    idO = models.BigAutoField(primary_key=True)
    sellerO = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='order_seller')
    buyerO = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='order_buyer')
    idG = models.ForeignKey(Goods, on_delete=models.CASCADE)
    quanO = models.FloatField()
    dateO = models.DateField()

    class Transaction:
        abstract = True
        idT = models.BigAutoField(primary_key=True)
        quanT = models.FloatField()
        dateT = models.DateField()
        priceT = models.FloatField()
