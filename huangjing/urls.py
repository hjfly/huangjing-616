# -*- coding: utf-8 -*-
"""
urls config
"""
from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
# admin.autodiscover()

# 公共URL配置
urlpatterns = patterns(
    'huangjing.views',
    (r'^$', 'contact_list'),
    (r'^test/api$', 'api_test'),
    (r'^schedule/manage', 'schedule_manage'),
    (r'^schedule/upload', 'schedule_upload'),
    (r'^api/schedule/upload', 'api_schedule_upload'),
    (r'^api/group/add', 'api_group_add'),
    (r'^api/holiday/add', 'api_holiday_add'),
    (r'^api/group/update', 'api_group_update'),
    (r'^api/holiday/update', 'api_holiday_update'),
    (r'^api/holiday/list', 'api_holiday_list'),
)
