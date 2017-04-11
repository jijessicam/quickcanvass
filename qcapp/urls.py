from django.conf.urls import url
from . import views
import django_cas_ng.views
import django_cas_ng

urlpatterns = [
    #url(r'^login/$', views.login, name='login'),
    url(r'^login_verification/$', views.login_verification, name='login_verification'),
    url(r'^accounts/signup/$', views.signup, name='signup'),
    url(r'^$', views.home, name='home'),
    url(r'^login$', views.login, name='login'),
    url(r'^create-new-account$', views.makeaccount, name='makeaccount'),
    url(r'^about/$', views.about, name = 'about'),
    url(r'^research/$', views.research, name = 'research'),
    #url(r'^contact/$', views.contact, name = 'contact'),
    url(r'^search/$', views.search, name = 'search'),
    url(r'^volunteerdash/(?P<netid>[A-Za-z0-9]+)/$', views.volunteerdash, name='volunteerdash'),
	url(r'^accounts/login/$', django_cas_ng.views.login, name='cas_ng_login'),
	url(r'^logout/$', django_cas_ng.views.logout, name='cas_ng_logout'),
    url(r'^accounts/callback$', django_cas_ng.views.callback, name='cas_ng_proxy_callback'),
    url(r'^volunteercampaigns/$', views.volunteercampaigns, name = 'volunteercampaigns'),
    url(r'^managerdash/$', views.managerdash, name = 'managerdash'),
    url(r'^editcampaign/$', views.editcampaign, name = 'editcampaign'),
]
