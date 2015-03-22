from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = patterns('',

    url(r'^$', 'radar.views.home', name='home'),
    url(r'^menu/', include('menu.urls', namespace='menu')),
    url(r'^orders/', include('orders.urls', namespace='orders')),
    url(r'^login/$', 'profiles.views.mylogin', name='login'),
    url(r'^register/$', 'profiles.views.register', name='register'),
    url(r'^logout/$', 'profiles.views.mylogout', name='logout'),
    url(r'^admin/my_admin_view/$', 'profiles.views.zip_import'),
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
