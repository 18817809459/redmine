from project.helper.helper import time_now
from king_ad.views import index_obj
from project import models


# 项目总数
def projects(request):
    project = models.Project.objects.all()
    if request.user.is_superuser:
        project = project
    elif request.user.is_admin:
        project = project.filter(department=request.user.department)
    else:
        ids = []
        project_users = models.ProjectUser.objects.filter(user=request.user)
        for project_user in project_users:
            ids.append(project_user.project_id)
        ids = list(set(ids))
        project = project.filter(id__in=ids)
    return project


# 完成的项目
def project_end(request):
    all_count = projects(request).count()
    count = projects(request).filter(status=3, examined=2).count()
    if all_count == 0:
        ratio = '0%'
    else:
        ratio = format(count / all_count, '.0%')
    data = {'count': count, 'ratio': ratio}
    return data


# 审核的项目
def project_examined_user(request):
    all_count = projects(request).count()
    count = projects(request).filter(status=0).count()
    if all_count == 0:
        ratio = '0%'
    else:
        ratio = format(count / all_count, '.0%')
    data = {'count': count, 'ratio': ratio}
    return data


# 执行中的项目
def project_execute(request):
    all_count = projects(request).count()
    count = projects(request).filter(status=1).count()
    if all_count == 0:
        ratio = '0%'
    else:
        ratio = format(count / all_count, '.0%')
    data = {'count': count, 'ratio': ratio}
    return data


# 已暂停项目
def project_pause(request):
    all_count = projects(request).count()
    count = projects(request).filter(status=5).count()
    if all_count == 0:
        ratio = '0%'
    else:
        ratio = format(count / all_count, '.0%')
    data = {'count': count, 'ratio': ratio}
    return data


# 已搁置项目
def project_shelve(request):
    all_count = projects(request).count()
    count = projects(request).filter(status=4).count()
    if all_count == 0:
        ratio = '0%'
    else:
        ratio = format(count / all_count, '.0%')
    data = {'count': count, 'ratio': ratio}
    return data


# 已延期项目
def project_postpone(request):
    all_count = projects(request).count()
    count = projects(request).filter(status=2).count()
    if all_count == 0:
        ratio = '0%'
    else:
        ratio = format(count / all_count, '.0%')
    data = {'count': count, 'ratio': ratio}
    return data


# 月新增项目（管理员，经理）
def project_month(request):
    year, month, day, week_start, week_end, week_list, dayscount, now = time_now()
    project = projects(request)
    project = project.filter(created_time__year=year, created_time__month=month)
    return project


# 周新增项目（管理员，经理）
def project_week(request):
    year, month, day, week_start, week_end, week_list, dayscount, now = time_now()
    project = projects(request)
    project = project.filter(created_time__range=([week_start, week_end]))
    return project


# 待审核项目（管理员，经理）
def project_examined(request):
    year, month, day, week_start, week_end, week_list, dayscount, now = time_now()
    project = models.Project.objects.all().filter(status=0)
    if request.user.is_admin:
        project = project.filter(department=request.user.department, examine=0)
    else:
        project = project.filter(examine=1)
    return project


# 周新增项目（个人）
def project_new_week(request):
    year, month, day, week_start, week_end, week_list, dayscount, now = time_now()
    project = projects(request)
    project = project.filter(id__in=ids, examined=2, created_time__range=([week_start, week_end]))
    return project


# 月完成项目（个人）
def project_end_month(request):
    year, month, day, week_start, week_end, week_list, dayscount, now = time_now()
    project = projects(request)
    project = project.filter(id__in=ids, status=3, examined=2, update_time__year=year, update_time__month=month)
    return project


# 月新增项目图表数据
def project_table():
    year, month, day, week_start, week_end, week_list, dayscount, now = time_now()
    project = models.Project.objects.all()
    data = []
    for index in range(1, 13):
        count = project.filter(created_time__year=year, created_time__month=index).count()
        js = {'day': str(index) + "月", 'project': count}
        data.append(js)
    return data


# 总览项目列表
def project_list(request):
    app_name = "project"
    table_name = "project"
    admin_class, query_sets, filter_condtions, orderby_key = index_obj(request, app_name, table_name)
    if request.user.is_superuser:
        query_sets = query_sets
    elif request.user.is_admin:
        query_sets = query_sets.filter(department=request.user.department)
    else:
        ids = [0]
        project_users = models.ProjectUser.objects.filter(user=request.user)
        for project_user in project_users:
            ids.append(project_user.project_id)
        ids = list(set(ids))
        query_sets = query_sets.filter(id__in=ids)
    query_sets = query_sets.order_by('-created_time')[:6]
    project_list = {'admin_class': admin_class, 'query_sets': query_sets, 'filter_condtions': filter_condtions,
                    'orderby_key': orderby_key}
    return project_list


# 总览图表
def project_chartist(request):
    year, month, day, week_start, week_end, week_list, dayscount, now = time_now()
    js = []
    project = projects(request)
    for index in range(1, 13):
        labels = str(index) + "月"
        series_one = project.filter(created_time__year=year, created_time__month=index).count()
        series_two = project.filter(status=3, update_time__year=year, update_time__month=index).count()
        js.append({'period': labels,'Sales': series_one,'Earning': series_two})
    return js
