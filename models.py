from django.db import models
from django.contrib.auth.models import User


# =============================================================================
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

class goods(models.Model):
    IdM
    NameM
    DurationM
    
class user(models.Model):
    IdU
    NameU
    PositionU
    ExpenseU
    ProfitU