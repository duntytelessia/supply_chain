from django.db import models
from django.contrib.auth.models import AbstractUser

#from django.contrib.auth import get_user_model
#User = get_user_model()
# =============================================================================
# =============================================================================

class CustomUser(AbstractUser):
    validate = models.BooleanField(default=False)


# class Week(models.Model):
#     week = models.PositiveIntegerField()
# 
#     def __str__(self):
#         return str(self.week) 
# 
# 
# class S_Product(models.Model):
# 
#     s_name = models.CharField(max_length=200, default='unknown_product')
#     s_user = models.ForeignKey(User, on_delete=models.CASCADE, default=2)
#     s_week = models.ForeignKey(Week, on_delete=models.CASCADE)
#     s_recieved = models.PositiveIntegerField()
#     s_sold = models.PositiveIntegerField()
#     s_command = models.PositiveIntegerField()
#     s_stock = models.PositiveIntegerField()
# 
#     def __str__(self):
#         return self.s_name
# 
# 
# class D_Product(models.Model):
# 
#     d_name = models.CharField(max_length=200, default='unknown_product')
#     d_user = models.ForeignKey(User, on_delete=models.CASCADE, default=2)
#     d_week = models.ForeignKey(Week, on_delete=models.CASCADE)
#     d_recieved = models.PositiveIntegerField()
#     d_sold = models.PositiveIntegerField()
#     d_command = models.PositiveIntegerField()
#     d_stock = models.PositiveIntegerField()
# 
#     def __str__(self):
#         return self.d_name
# =============================================================================

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
