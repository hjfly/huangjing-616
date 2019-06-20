# -*- coding: utf-8 -*-

from common.mymako import render_json
from common.mymako import render_mako_context
import datetime
from models import User
from conf.default import APP_TOKEN, APP_ID
from blueking.component.shortcuts import get_client_by_request
from django.db.models import Q


def api_test(request):
    return render_json({'result': 'true', 'username': request.user.username,
                        "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})


def contact_list(request):
    users = User.objects.all()
    if not users:
        client = get_client_by_request(request)
        kwargs = {'bk_app_secret': APP_TOKEN, 'bk_app_code': APP_ID}
        result_user = client.bk_login.get_all_users(kwargs)
        if result_user['result'] and result_user['data']:
            for user in result_user['data']:
                user = {
                    'role': user['bk_role'],
                    'username': user['bk_username'],
                    'loginname': user['chname'],
                    'mobile': user['phone'],
                    'email': user['email']
                }
                User.objects.create(**user)

    q_query = Q()
    username = request.GET.get("username")
    if username:
        q_query = q_query & Q(username__icontains=username)
    result_list = User.objects.filter(q_query).values()
    loginuser = User.objects.filter(loginname=request.user.username).values()[0]
    if loginuser['role'] == '1':
        is_admin = True
    else:
        is_admin = False
    result_users = []
    if result_list:
        result_users = list(result_list)

    return render_mako_context(request, '/huangjing/contact-list.html', {'result_users': result_users,'is_admin': is_admin})


def schedule_manage(request):
    return render_mako_context(request, '/huangjing/schedule-manage.html')
