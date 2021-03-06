from django.db import models
from django.utils import timezone

tz = timezone.get_default_timezone()


class Class(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    subject = models.CharField(max_length=100, blank=True)
    classes = models.ManyToManyField(Class, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.email} - {self.subject} " \
               f"({' '.join(elem.name for elem in self.classes.all())})"


class Parent(models.Model):
    token = models.CharField(max_length=100, unique=True)
    parent_name = models.CharField(max_length=100)
    parent_email = models.EmailField(max_length=100)
    student_grade = models.CharField(max_length=10)
    student_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.parent_name} - {self.student_name}"


class Appointment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    comment = models.CharField(max_length=1000)

    def __str__(self):
        return f"{self.teacher.name} - {self.parent.parent_name} ({self.parent.student_name}, {self.parent.student_grade})"


class OpenDay(models.Model):
    datetime = models.DateTimeField()

    def date(self):
        return self.datetime.astimezone(tz).strftime('%d.%m.%Y')

    def time(self):
        return self.datetime.astimezone(tz).strftime('%H:%M')

    def __str__(self):
        return 'День открытых дверей от {}'.format(self.datetime.astimezone(tz).strftime('%d.%m.%Y %H:%M'))
