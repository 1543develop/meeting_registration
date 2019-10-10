from django.db import models


class Student(models.Model):
    student_name = models.CharField(max_length=100)
    relative_name = models.CharField(max_length=100)
    grade = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=100)
    email = models.EmailField()


class Teachers(models.Model):
    name = models.CharField(max_length=100)
    list_of_grades = models.CharField(max_length=100)
    cabinet = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    number_of_visitors = models.IntegerField()
    list_of_visitors = models.ManyToManyField(Student)
    workload = models.IntegerField()  # Three levels: 0 (<= 5), 1 (<=10), 2 (<=15)


