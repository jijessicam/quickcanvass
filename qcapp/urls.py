from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^create-new-account$', views.makeaccount, name='makeaccount'),
    url(r'^about/$', views.about, name = 'about'),
    url(r'^research/$', views.research, name = 'research'),
    url(r'^contact/$', views.contact, name = 'contact'),
    url(r'^search/$', views.search, name = 'contact'),
    url(r'^volunteerdash/$', views.volunteerdash, name='volunteerdash')

]