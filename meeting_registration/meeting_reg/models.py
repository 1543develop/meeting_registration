from django.db import models


class Student(models.Model):
    name = models.CharField(max_length=100)
    relative = models.CharField(max_length=100)
    grade = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=100)
    email = models.EmailField()

    class Meta:
        ordering = ["grade", "name"]

    def __str__(self):
        return f"{self.name} {self.grade}"


class Form(models.Model):
    parent_name = models.CharField(max_length=100)
    parent_email = models.EmailField(max_length=100)
    student_grade = models.CharField(max_length=10)
    student_name = models.CharField(max_length=100)
    teacher_names = models.CharField(max_length=1000)


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    list_of_grades = models.CharField(max_length=100)
    cabinet = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    number_of_visitors = models.IntegerField()
    list_of_visitors = models.ManyToManyField(Student)
    workload = models.IntegerField()  # Three levels: 0 (<= 5), 1 (<=10), 2 (<=15)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
