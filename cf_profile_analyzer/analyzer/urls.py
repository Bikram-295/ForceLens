from django.urls import path
from . import views

urlpatterns = [
    path('', views.single, name='single'),
    path('dual', views.dual, name='dual')
]
