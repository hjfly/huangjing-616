# -*- coding: utf-8 -*-

from common.mymako import render_json
from common.mymako import render_mako_context
import datetime
from models import User
from conf.default import APP_TOKEN, APP_ID
from blueking.component.shortcuts import get_client_by_request


def api_test(request):
    return render_json({'result': 'true', 'username': request.user.username,
                        "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})


def index(request):
    user = User.objects.all()
    if not user:
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

    return render_mako_context(request, '/huangjing/contact-list.html')


def contactus(request):
    """
    联系我们
    """
    return render_mako_context(request, '/home_application/contact.html')
