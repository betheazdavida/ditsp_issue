from django.conf.urls import url

from . import views

app_name = 'complaintManager'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^complaints/create/$', views.complaint_create, name='complaint_create'),
    url(r'^submit/$', views.complaint_create_public, name='complaint_create_public'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^complaints/$', views.complaint_list, name='complaint_list'),
    url(r'^complaints/out/$', views.complaint_list_out, name='complaint_list_out'),
    url(r'^complaints/public/$', views.complaint_list_public, name='complaint_list_public'),
    url(r'^complaints/(?P<pk>[0-9]+)/$', views.complaint_status, name='complaint_status'),
    url(r'^complaints/(?P<pk>[0-9]+)/edit/$', views.complaint_edit, name='complaint_edit'),
    url(r'^complaints/(?P<pk>[0-9]+)/delete/$', views.complaint_delete, name='complaint_delete'),
    url(r'^informer_origins/$', views.informer_origin_index, name='informer_origin_index'),
    url(r'^informer_origins/add$', views.informer_origin_add, name='informer_origin_add'),
    url(r'^informer_origins/(?P<pk>[0-9]+)/delete$', views.informer_origin_delete, name='informer_origin_delete'),
    url(r'^informer_origins/(?P<pk>[0-9]+)/edit$', views.informer_origin_edit, name='informer_origin_edit'),
    url(r'^users/$', views.user_index, name='user_index'),
    url(r'^users/create/$', views.user_create, name='user_create'),
    url(r'^users/(?P<pk>[0-9]+)/edit/$', views.user_edit, name='user_edit'),
    url(r'^users/(?P<pk>[0-9]+)/delete/$', views.user_delete, name='user_delete'),
    url(r'^updatestatus/(?P<pk>[0-9]+)/$', views.update_status, name='update_status'),
    url(r'^addworker/(?P<pk>[0-9]+)/$', views.add_worker, name='add_worker'),
    url(r'^addlog/(?P<pk>[0-9]+)/$', views.add_log, name='add_log'),
    url(r'^editlog/(?P<pk>[0-9]+)/$', views.edit_log, name='edit_log'),
    url(r'^deletelog/(?P<pk>[0-9]+)/$', views.delete_log, name='delete_log'),
    url(r'^addimagelog/(?P<pk>[0-9]+)/$', views.add_image_log, name='add_image_log'),
    url(r'^laporan/$', views.laporan, name='laporan'),
]
