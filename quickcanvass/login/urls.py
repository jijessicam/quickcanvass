from django.conf.urls import url, include
from login import views
urlpatterns = [

<<<<<<< HEAD
    url(r'^login$', views.login, name = 'login'),
    url(r'^signup$', views.signup, name = 'signup'),
    url(r'^create-new-account$', views.makeaccount, name='create-new-account')
=======
    url(r'^$', views.index, name = 'index'),
>>>>>>> 9115f1291f39d876e567becad2426e3051e58cfa
]
