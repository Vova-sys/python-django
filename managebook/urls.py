from django.urls import path

from managebook import views

urlpatterns = [
    path('hello/', views.hello, name='hello')
]
