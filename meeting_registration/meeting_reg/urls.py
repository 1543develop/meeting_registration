"""meeting_registration URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', views.registration),
    path('thanks', views.thanks_page),
    path('update/<str:token>', views.re_registration),
    path('teacher_mailing', views.teacher_mailing),
    path('parent_mailing', views.parent_mailing),
    path('import', views.upload_teachers_to_db),
    path('admin', admin.site.urls),
    path('teachers', views.all_teachers),
    path('classes', views.all_classes),
    path('clear', views.clear_db),
    path('clear_appointments', views.new_day),
    path('teachers_dump', views.appointments_dump_for_teachers),
    path('parents_dump', views.appointments_dump_for_parent),
    path('teachers/<str:grade>', views.teachers_by_grade),
    path('panel', views.manip_panel),
]
