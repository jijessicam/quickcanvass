from django.conf.urls import url, include
from login import views
urlpatterns = [

    url(r'^$', views.index, name = 'index'),
]
