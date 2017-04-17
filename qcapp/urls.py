from django.conf.urls import url
from . import views
import django_cas_ng.views
import django_cas_ng

urlpatterns = [
    #url(r'^login/$', views.login, name='login'),
    url(r'^login_verification/$', views.login_verification, name='login_verification'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^$', views.home, name='home'),
    url(r'^login/$', views.login, name='login'),
    url(r'^create-new-account$', views.makeaccount, name='makeaccount'),
    url(r'^about/$', views.about, name = 'about'),
    url(r'^research/$', views.research, name = 'research'),
    #url(r'^contact/$', views.contact, name = 'contact'),
    url(r'^search/$', views.search, name = 'search'),
    url(r'^volunteerdash/(?P<netid>[A-Za-z0-9]+)/$', views.volunteerdash, name='volunteerdash'),
	url(r'^accounts/login/$', django_cas_ng.views.login, name='cas_ng_login'),
	url(r'^logout/$', django_cas_ng.views.logout, name='cas_ng_logout'),
    url(r'^accounts/callback$', django_cas_ng.views.callback, name='cas_ng_proxy_callback'),
    url(r'^volunteercampaigns/(?P<campaign_id>[0-9]+)/(?P<netid>[A-Za-z0-9]+)/$', views.volunteercampaigns, name = 'volunteercampaigns'),
    url(r'^managerdash/(?P<netid>[A-Za-z0-9]+)/$', views.managerdash, name = 'managerdash'),
    url(r'^editcampaign/$', views.editcampaign, name = 'editcampaign'),
    url(r'^join-new-campaign/$', views.join_new_campaign, name='join_new_campaign'),
    url(r'^editsurvey/$', views.editsurvey, name = 'editsurvey'),
    url(r'^fillsurvey/(?P<campaign_id>[0-9]+)/(?P<netid>[A-Za-z0-9]+)/$', views.fillsurvey, name = 'fillsurvey'),
    ## fillsurvey url not complete
]
