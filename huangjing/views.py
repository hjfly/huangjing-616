# -*- coding: utf-8 -*-

from common.mymako import render_json
from common.mymako import render_mako_context
import datetime
from models import User
from conf.default import APP_TOKEN, APP_ID, FILE_UPLOAD_PATH
from blueking.component.shortcuts import get_client_by_request
from django.db.models import Q
import xlrd
from models import Group
from models import Holiday
from models import Scheduled
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


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

    return render_mako_context(request, '/huangjing/contact-list.html',
                               {'result_users': result_users, 'is_admin': is_admin})


def schedule_manage(request):
    group_list = []
    result_list = Group.objects.values()
    if result_list:
        group_list = list(result_list)
    return render_mako_context(request, '/huangjing/schedule-manage.html', {'group_list': group_list})


def schedule_upload(request):
    request_month = request.POST.get('month', '六月')
    MONTH = {1: '一月', 2: '二月', 3: '三月', 4: '四月', 5: '五月', 6: '六月', 7: '七月', 8: '八月', 9: '九月', 10: '十月', 11: '十一月',
             12: '十二月'}
    WEEK = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    if not request_month:
        month = datetime.datetime.now().month
        for key in MONTH:
            if key == month:
                request_month = MONTH[key]
    scheduled = Scheduled.objects.filter(month=request_month).order_by('-day').values()
    group_scheduled = []
    if scheduled and len(list(scheduled)) > 0:
        day = scheduled[0]['day']
        first_day_scheduled = Scheduled.objects.filter(day=1).values()[0]
        group_ids = Scheduled.objects.filter(day=1).values('group_id').distinct()
        groups = []
        for group_id in group_ids:
            group = Group.objects.get(id=group_id['group_id'])
            groups.append(group.name)

        first_week_index = WEEK.index(first_day_scheduled['week'])
        temp = []
        flag = True
        for k in xrange(0, len(groups) + 1):
            temp.append('')

        temp_data = {}
        if first_week_index > 0:
            for j in xrange(0, first_week_index):
                temp_data['week' + str(j)] = temp
        data = {}
        last_week_index = 0
        for i in xrange(1, day+1):
            scheduled = Scheduled.objects.filter(day=i).values()[0]
            user_array = [i]
            for group_id in group_ids:
                users = Scheduled.objects.filter(day=i, group_id=group_id['group_id']).values()
                temp_user = ''
                for user in users:
                    user_obj = User.objects.get(id=user['user_id'])
                    temp_user += user_obj.username + '、'
                user_array.append(temp_user)

            if first_week_index != 0 and flag:
                data = temp_data
                flag = False
            current_week_index = WEEK.index(scheduled['week'])
            last_week_index = current_week_index
            data['week' + str(current_week_index)] = user_array
            if scheduled['week'] == '周六':
                data['time'] = '日期'
                data['groups'] = groups
                group_scheduled.append(data)
                data = {}

        if last_week_index != 6:
            data['time'] = '日期'
            data['groups'] = groups
            group_scheduled.append(data)
    return render_mako_context(request, '/huangjing/schedule-upload.html', {'scheduled_list': group_scheduled})


def api_schedule_upload(request):
    """处理上传文件"""
    wb = xlrd.open_workbook(filename=None, file_contents=request.FILES['file'].read())  # 关键点在于这里
    # col = table.row_values(i) 行内容
    sheet = wb.sheets()[0]
    row = sheet.nrows
    col = sheet.ncols
    title = sheet.row(0)[4].value
    year = title[0:4]
    month = title[5:7]
    for i in xrange(4, row, 5):
        for j in xrange(4, col):
            if sheet.row(i)[j].value:
                day = sheet.row(i)[j].value
                week = sheet.row(3)[j].value
                for k in xrange(1, 5):
                    group_id = sheet.row(i + k)[3].value
                    loginnames = sheet.row(i + k)[j].value
                    if loginnames:
                        for loginname in loginnames.split('、'):
                            scheduled = Scheduled()
                            user = User.objects.get(loginname=loginname)
                            scheduled.user_id = user.id
                            scheduled.month = month
                            scheduled.year = year
                            scheduled.day = int(day)
                            scheduled.group_id = int(group_id)
                            scheduled.week = week
                            scheduled.save()

    return render_mako_context(request, '/huangjing/schedule-upload.html')


def api_group_add(request):
    name = request.POST.get('name')
    order = request.POST.get('order')
    group = {
        'name': name,
        'order': order
    }
    Group.objects.create(**group)
    return render_json({'success': True})


def api_holiday_add(request):
    name = request.POST.get('name')
    time = request.POST.get('time')
    holiday = Holiday(name=name)
    holiday.data = time
    holiday.year = time.split('-')[0]
    holiday.save()
    return render_json({'success': True})


def api_group_update(request):
    name = request.POST.get('name')
    id = request.POST.get('id')
    group = Group.objects.get(id=id)
    group.name = name
    group.save()
    return render_json({'success': True})


def api_holiday_update(request):
    name = request.POST.get('name')
    id = request.POST.get('id')
    holiday = Holiday.objects.get(id=id)
    holiday.name = name
    holiday.save()
    return render_json({'success': True})


def api_holiday_list(request):
    holiday_list = []
    q_query = Q()
    year = request.POST.get("year")
    if year:
        q_query = q_query & Q(year=year)
    result_list = Holiday.objects.filter(q_query).values()

    if result_list:
        holiday_list = list(result_list)
    return render_json({"success": True, "data": holiday_list})


def file_upload(request):
    if not os.path.exists(FILE_UPLOAD_PATH):
        os.makedirs(FILE_UPLOAD_PATH)
    """处理上传文件"""
    filedata = request.FILES.get('file')
    if filedata.file:
        file_path = os.path.join(FILE_UPLOAD_PATH, filedata.name)
        try:
            f = open(file_path, 'wb')
            for chunk in filedata.chunks():
                f.write(chunk)
            f.close()
        except IOError:
            return '上传文件失败'
        return '上传文件成功, 文件名: ' + file_path
    else:
        return '上传文件失败'

def schedule_statistics(request):
    return render_mako_context(request,'/huangjing/schedule-statistics.html')


def api_schedule_statistics(request):
    return render_json({'success': True})
