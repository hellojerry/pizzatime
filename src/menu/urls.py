from django.conf.urls import patterns, include, url
from django.contrib import admin
#from .views import MenuGroupView

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'menu.views.menu_home', name='menu_home'),
    (r'menu_home/check_address$', 'menu.views.check_address'),
    (r'menu_home/change_address$', 'menu.views.change_address'),
    (r'menu_home/add_pizza$', 'menu.views.add_pizza'),
    (r'menu_home/delete_line_item/(?P<id>\d+)$', 'menu.views.delete_line_item'),
    (r'menu_home/edit_line_item$', 'menu.views.edit_line_item'),
    (r'menu_home/add_note$', 'menu.views.add_note'),
    url(r'^set_pickup/$', 'menu.views.set_pickup', name='set_pickup'),
    url(r'^set_delivery/$', 'menu.views.set_delivery', name='set_delivery'),
    url(r'^add_entree/(?P<id>\d+)/$', 'menu.views.add_entree', name='add_entree'),
    #url(r'^(?P<exp>[PSODBTWHE])$', MenuGroupView.as_view(), name='menu_group'),
    url(r'^(?P<exp>[PSODBTWHEG])/$', 'menu.views.menu_group', name='menu_group'),
    (r'(?P<exp>[PSODBTWHEG])/edit_product$', 'menu.views.edit_product'),
    (r'(?P<exp>[PSODBTWHEG])/create_product$', 'menu.views.create_product'),
)
#url(r'^order_status/$', 'orders.views.order_status', name='order_status'),



