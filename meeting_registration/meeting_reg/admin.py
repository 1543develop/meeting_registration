from django.contrib import admin
from .models import Teacher, Parent, Appointment, Class, OpenDay

admin.site.register(Teacher)
admin.site.register(Parent)
admin.site.register(Appointment)
admin.site.register(Class)
admin.site.register(OpenDay)
