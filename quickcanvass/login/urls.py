from django.conf.urls import url, include
from login import views
urlpatterns = [

    url(r'^login$', views.login, name = 'login'),
    url(r'^signup$', views.signup, name = 'signup'),
    url(r'^create-new-account$', views.makeaccount, name='create-new-account')
]
