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
    url(r'^search_by_ids/$', views.search_by_ids, name = 'search_by_ids'),
    url(r'^search/$', views.search, name = 'search'),
    url(r'^volunteerdash/(?P<netid>[A-Za-z0-9_]+)/$', views.volunteerdash, name='volunteerdash'),
	url(r'^accounts/login/$', django_cas_ng.views.login, name='cas_ng_login'),
	url(r'^logout/$', views.logout, name='cas_ng_logout'),
    url(r'^accounts/callback$', django_cas_ng.views.callback, name='cas_ng_proxy_callback'),
    url(r'^volunteercampaigns/(?P<campaign_id>[0-9]+)/(?P<netid>[A-Za-z0-9_]+)/$', views.volunteercampaigns, name = 'volunteercampaigns'),
    url(r'^managerdash/(?P<netid>[A-Za-z0-9_]+)/$', views.managerdash, name = 'managerdash'),
    url(r'^editcampaign/(?P<netid>[A-Za-z0-9_]+)$', views.editcampaign, name = 'editcampaign'),
    url(r'^promote-to-manager/(?P<netid>[A-Za-z0-9_]+)/$', views.promote_to_manager, name = 'promote_to_manager'),
    url(r'^join-new-campaign/$', views.join_new_campaign, name='join_new_campaign'),
    url(r'^editsurvey/(?P<netid>[0-9]+)/$', views.editsurvey, name = 'editsurvey'),
    url(r'^fillsurvey/(?P<campaign_id>[0-9]+)/(?P<netid>[A-Za-z0-9_]+)/(?P<voter_id>[0-9]+)$', views.fillsurvey, name = 'fillsurvey'),
    url(r'^download_survey_data/$', views.download_survey_data, name = 'download_survey_data'),
    url(r'^clear_survey_data/$', views.clear_survey_data, name='clear_survey_data'),
    url(r'^about/$', views.about, name='about'),
    
    ## fillsurvey url not complete
]
