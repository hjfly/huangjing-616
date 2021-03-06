# -*- coding: utf-8 -*-

from common.mymako import render_json
from common.mymako import render_mako_context
import datetime
from models import User
from conf.default import APP_TOKEN, APP_ID, FILE_UPLOAD_PATH
from blueking.component.shortcuts import get_client_by_request
from django.db.models import Q,Max
import xlrd
from models import Group
from models import Holiday
from models import Scheduled
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

MONTH = {1: '一月', 2: '二月', 3: '三月', 4: '四月', 5: '五月', 6: '六月', 7: '七月', 8: '八月', 9: '九月', 10: '十月', 11: '十一月',
         12: '十二月'}

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
    WEEK = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    if not request_month:
        month = datetime.datetime.now().month
        for key in MONTH:
            if key == month:
                request_month = MONTH[key]
    scheduled = Scheduled.objects.filter(month=request_month).all().aggregate(Max('day'))
    group_scheduled = []
    if scheduled and scheduled['day__max']:
        day = scheduled['day__max']
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
    users = User.objects.all()
    groups = Group.objects.all()
    return render_mako_context(request,'/huangjing/schedule-statistics.html',{'users': users, 'groups': groups})


def api_schedule_statistics(request):
    user_id = request.POST.get('user_id')
    group_id = request.POST.get('group_id')
    q_query = Q()
    q_q = Q()
    if user_id:
        q_query = q_query & Q(user_id=user_id)
        q_q = q_q & Q(user_id=user_id)
    if group_id:
        q_query = q_query & Q(group_id=group_id)
        q_q = q_q & Q(group_id=group_id)

    holidays = Holiday.objects.all()
    statistic_holiday =[]
    statistic_normal =[]
    for holiday in holidays:
        date = holiday.data
        str = date.split('-')
        month_key = int(str[1])
        month_value = MONTH[month_key]
        day = int(str[2])
        q_query = q_query & Q(month=month_value)
        q_query = q_query & Q(day=day)
        holiday_schedules = Scheduled.objects.filter(q_query).values()
        holiday_days = 0
        if holiday_schedules:
            holiday_days = len(list(holiday_schedules))
        flag = True
        for sta in statistic_holiday:
            if sta['month'] == month_key:
                sta['day'] = sta['day'] + holiday_days
                flag = False
        if flag:
            statistic_holiday.append({'month': month_key, 'day': holiday_days})

    for holiday in holidays:
        date = holiday.data
        str = date.split('-')
        month_key = int(str[1])
        month_value = MONTH[month_key]
        q_q = q_q & Q(month=month_value)
        schedules = Scheduled.objects.filter(q_q).values()
        sum_days = 0
        if schedules:
           sum_days = len(list(schedules))
        flag = True
        for sta in statistic_holiday:
            if sta['month'] == month_key:
                statistic_normal.append({'month': month_key, 'day': sum_days - sta['day']})
                flag = False

        if flag:
            statistic_normal.append({'month': month_key, 'day': sum_days})

    normals = []
    holidays = []
    for key in MONTH.keys():
        flag = True
        for normal in statistic_normal:
            if normal['month'] == key:
                normals.append(normal['day'])
                flag = False
                break
        if flag:
            normals.append(0)

        holiday_flag = True
        for holiday in statistic_holiday:
            if holiday['month'] == key:
                holidays.append(holiday['day'])
                holiday_flag = False
                break
        if holiday_flag:
            holidays.append(0)

    data_line = {
        "xAxis": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
        "series": [
            {
                "name": "节假日",
                "type": "line",
                "data": holidays
            },
            {
                "name": "工作日",
                "type": "line",
                "data": normals
            }
        ]

    }
    data_ebar = {
        "xAxis": [{
            "type": "category",
            "data": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
        }],
        "series": [{
            "name": "节假日",
            "type": "bar",
            "data": holidays
        }, {
            "name": "工作日",
            "type": "bar",
            "data": normals
        }]
    }
    data = []
    if user_id:
        data = data_line
    if group_id:
        data = data_ebar
    return render_json({'result': True, 'data': data})
