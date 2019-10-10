from django.db import models


class Teachers(models.Model):
    name = models.CharField()
    list_of_grades = models.CharField()
    cabinet = models.CharField()
    phone_number = models.CharField()
    email = models.EmailField()
    number_of_visitors = models.IntegerField()
    workload = models.IntegerField() #Three levels: 0 (<= 5), 1 (<=10), 2 (<=15)
