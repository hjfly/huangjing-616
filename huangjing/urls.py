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
)
