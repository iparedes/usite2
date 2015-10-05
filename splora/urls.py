__author__ = 'nacho'

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^loadxml$', views.loadxml, name='loadxml,'),
    url(r'^newsun$', views.newsun, name='newsun'),
    url(r'^newsector$', views.newsector, name='newsector'),
]

