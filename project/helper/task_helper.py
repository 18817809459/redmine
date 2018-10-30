from project.helper.helper import time_now
from king_ad.views import index_obj
from project import models
import datetime
from project.helper.project_helper import projects


# 任务总数
def taskes(request):
    project = projects(request)
    task = models.Task.objects.all()
    if request.user.is_superuser:
        task = task
    elif request.user.is_admin:
        task = task.filter(project__in=project)
    else:
        ids = []
        task_users = models.TaskUser.objects.filter(user=request.user)
        for task_user in task_users:
            ids.append(task_user.task_id)
        ids = list(set(ids))
        task = task.filter(id__in=ids)
    return task


# 完成的任务
def task_end(request):
    all_count = taskes(request).count()
    count = taskes(request).filter(status=3).count()
    if all_count == 0:
        ratio = '0%'
    else:
        ratio = format(count / all_count, '.0%')
    data = {'count': count, 'ratio': ratio}
    return data


# 待执行任务
def task_examined_user(request):
    all_count = taskes(request).count()
    count = taskes(request).filter(status=0).count()
    if all_count == 0:
        ratio = '0%'
    else:
        ratio = format(count / all_count, '.0%')
    data = {'count': count, 'ratio': ratio}
    return data


# 执行中的任务
def task_execute(request):
    all_count = taskes(request).count()
    count = taskes(request).filter(status=1).count()
    if all_count == 0:
        ratio = '0%'
    else:
        ratio = format(count / all_count, '.0%')
    data = {'count': count, 'ratio': ratio}
    return data


# 已暂停任务
def task_pause(request):
    all_count = taskes(request).count()
    count = taskes(request).filter(status=5).count()
    if all_count == 0:
        ratio = '0%'
    else:
        ratio = format(count / all_count, '.0%')
    data = {'count': count, 'ratio': ratio}
    return data


# 已搁置任务
def task_shelve(request):
    all_count = taskes(request).count()
    count = taskes(request).filter(status=4).count()
    if all_count == 0:
        ratio = '0%'
    else:
        ratio = format(count / all_count, '.0%')
    data = {'count': count, 'ratio': ratio}
    return data


# 已延期任务
def task_postpone(request):
    all_count = taskes(request).count()
    count = taskes(request).filter(status=2).count()
    if all_count == 0:
        ratio = '0%'
    else:
        ratio = format(count / all_count, '.0%')
    data = {'count': count, 'ratio': ratio}
    return data


# 今日新增任务（管理员，经理）
def task_day(request):
    year, month, day, week_start, week_end, week_list, dayscount, now = time_now()
    task = models.Task.objects.all()
    ids = []
    if request.user.is_admin:
        department_id = request.user.department_id
        projects = models.Project.objects.filter(department=department_id)
        for project in projects:
            taskes = models.Task.objects.filter(project=project)
            for taske in taskes:
                ids.append(taske.id)
        ids = list(set(ids))
        task = task.filter(id__in=ids)
    task = task.filter(created_time__year=year, created_time__month=month, created_time__day=day)
    return task


# 本周新增任务（管理员，经理）
def task_week(request):
    year, month, day, week_start, week_end, week_list, dayscount, now = time_now()
    task = models.Task.objects.all()
    ids = []
    if request.user.is_admin:
        department_id = request.user.department_id
        projects = models.Project.objects.filter(department=department_id)
        for project in projects:
            taskes = models.Task.objects.filter(project=project)
            for taske in taskes:
                ids.append(taske.id)
        ids = list(set(ids))
        task = task.filter(id__in=ids)
    task = task.filter(created_time__range=([week_start, week_end]))
    return task


# 今日新增任务（个人）
def task_new_day(request):
    year, month, day, week_start, week_end, week_list, dayscount, now = time_now()
    task = models.Task.objects.all()
    ids = []
    task_users = models.TaskUser.objects.filter(user=request.user)
    for task_user in task_users:
        ids.append(task_user.task_id)
    ids = list(set(ids))
    task = task.filter(id__in=ids, created_time__year=year, created_time__month=month, created_time__day=day)
    return task


# 本周完成任务（个人）
def task_end_week(request):
    year, month, day, week_start, week_end, week_list, dayscount, now = time_now()
    task = models.Task.objects.all()
    ids = []
    task_users = models.TaskUser.objects.filter(user=request.user)
    for task_user in task_users:
        ids.append(task_user.task_id)
    ids = list(set(ids))
    task = task.filter(id__in=ids, update_time__range=([week_start, week_end]), status=3)
    return task


# 周新增任务图标数据
def task_table():
    year, month, day, week_start, week_end, week_list, dayscount, now = time_now()
    task = models.Task.objects.all()
    data = []
    for index, week in enumerate(week_list):
        num = index + 1
        week_day = now - dayscount + datetime.timedelta(days=num)
        count = task.filter(created_time__year=week_day.year, created_time__month=week_day.month,
                            created_time__day=week_day.day).count()
        js = {'day': week, 'task': count}
        data.append(js)
    return data


# 新增任务列表
def task_new_list(request):
    app_name = "project"
    table_name = "task"
    admin_class, query_sets, filter_condtions, orderby_key = index_obj(request, app_name, table_name)
    ids = []
    task_users = models.TaskUser.objects.filter(user=request.user)
    create_tasks = models.Task.objects.filter(created_user=request.user)
    for create_task in create_tasks:
        ids.append(create_task.id)
    for task_user in task_users:
        ids.append(task_user.task_id)
    ids = list(set(ids))
    query_sets = query_sets.filter(id__in=ids, status__in=[0])
    count = query_sets.count()
    query_sets = query_sets.order_by('-created_time')[:3]
    task_new_list = {'admin_class': admin_class, 'query_sets': query_sets, 'filter_condtions': filter_condtions,
                     'orderby_key': orderby_key, 'count': count}
    return task_new_list


# 延期任务列表
def task_delay_list(request):
    app_name = "project"
    table_name = "task"
    admin_class, query_sets, filter_condtions, orderby_key = index_obj(request, app_name, table_name)
    ids = []
    task_users = models.TaskUser.objects.filter(user=request.user)
    create_tasks = models.Task.objects.filter(created_user=request.user)
    for create_task in create_tasks:
        ids.append(create_task.id)
    for task_user in task_users:
        ids.append(task_user.task_id)
    ids = list(set(ids))
    query_sets = query_sets.filter(id__in=ids, status=2)
    count = query_sets.count()
    query_sets = query_sets.order_by('-created_time')[:3]
    task_delay_list = {'admin_class': admin_class, 'query_sets': query_sets, 'filter_condtions': filter_condtions,
                       'orderby_key': orderby_key, 'count': count}
    return task_delay_list


# 折线图表数据
def task_chartist(request):
    year, month, day, week_start, week_end, week_list, dayscount, now = time_now()
    task = taskes(request)
    js = []
    for index, week in enumerate(week_list):
        num = index + 1
        week_day = now - dayscount + datetime.timedelta(days=num)
        task_new = task.filter(created_time__year=week_day.year, created_time__month=week_day.month,
                               created_time__day=week_day.day).count()
        task_end = task.filter(status=3, update_time__year=week_day.year, update_time__month=week_day.month,
                               update_time__day=week_day.day).count()
        js.append({'period': week, 'Sales': task_new, 'Earning': task_end})
    return js
