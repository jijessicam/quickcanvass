from django.conf.urls import url, include
from search import views
urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    #url(r'^searchlocation/', include('searchlocation.urls')),
    url(r'^$', views.index, name = 'index'),
]
