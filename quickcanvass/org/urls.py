from django.conf.urls import url, include
from org import views
urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    #url(r'^searchlocation/', include('searchlocation.urls')),
    url(r'^$', views.index, name = 'index'),
    url(r'^about/$', views.about, name = 'about'),
]
