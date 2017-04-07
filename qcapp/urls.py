from django.conf.urls import url
from . import views
import django_cas_ng.views

urlpatterns = [
    #url(r'^login/$', views.login, name='login'),
    url(r'^login_verification/$', views.login_verification, name='login_verification'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^$', views.signup, name='signup'),
    url(r'^create-new-account$', views.makeaccount, name='makeaccount'),
    url(r'^about/$', views.about, name = 'about'),
    url(r'^research/$', views.research, name = 'research'),
    url(r'^contact/$', views.contact, name = 'contact'),
    url(r'^search/$', views.search, name = 'search'),
    url(r'^volunteerdash/$', views.volunteerdash, name='volunteerdash'),
	url(r'^login/$', django_cas_ng.views.login, name='cas_ng_login'),
	url(r'^logout/$', django_cas_ng.views.logout, name='cas_ng_logout'),
    url(r'^accounts/callback$', django_cas_ng.views.callback, name='cas_ng_proxy_callback'),
]