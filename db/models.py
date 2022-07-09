from datetime import datetime
import sys

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()


from django.core.validators import MaxValueValidator

# Sample User model
# class Worker(models.Model):
#     name = models.CharField(max_length=50, default="Dan")
#     rate = models.DecimalField(default=10,decimal_places=1) 
#     def __str__(self):
#         return self.name

class User(models.Model):
    user_id = models.CharField(max_length=50,blank=True,null=True)
    number = models.CharField(max_length=50) 
    def __str__(self):
        return self.number


class Service(models.Model):
    # price  = models.DecimalField(decimal_places=2)
    # start_time = models.DateTimeField(default=datetime.now())
    end_time = models.DateTimeField(default=datetime.now)
    # worker = models.ForeignKey(User,on_delete=models.CASCADE)
    number = models.CharField(max_length=20)


class Discount(models.Model):
    count = models.PositiveBigIntegerField() 
    percent = models.PositiveBigIntegerField(validators=[MaxValueValidator(100)]) 
