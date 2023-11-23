from django.urls import path

from . import views

app_name = 'custom_forms'

urlpatterns = [
    path('get_form/', views.get_form, name='get_form'),
]
