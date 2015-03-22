from django.conf.urls import patterns, include, url
from django.contrib import admin
from orders.views import OrderSuccessView

urlpatterns = patterns('',
    # Examples:
    url(r'^(?P<id>\d+)/$', 'orders.views.auth_checkout', name='auth_checkout'),
    url(r'^add_info/(?P<id>\d+)$', 'orders.views.add_info', name='add_info'),
    url(r'^receipt_email/(?P<id>\d+)/$', 'orders.views.receipt_email', name='receipt_email'),
    (r'/check_address$', 'menu.views.check_address'),
    url(r'^company_home/$', 'orders.views.company_home', name='company_home'),
    url(r'^order_dashboard/$', 'orders.views.order_dashboard', name='order_dashboard'),

    url(r'^order_status/$', 'orders.views.order_status', name='order_status'),
    url(r'^order_reverse/$', 'orders.views.order_reverse', name='order_reverse'),
    url(r'^order_success/(?P<pk>\d+)/$', OrderSuccessView.as_view(), name='order_success'),
)