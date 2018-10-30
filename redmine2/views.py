from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from project.helper import project_helper,task_helper
import json
# from dwebsocket import require_websocket
# import time
# Django的form的作用：
# 1、生成html标签
# 2、用来做用户提交的验证
# Form的验证思路
# 前端：form表单
# 后台：创建form类，当请求到来时，先匹配，匹配出正确和错误信息。

@login_required(login_url='/login/')
def index(request):
    project_list = project_helper.project_list(request)
    task_new_list = task_helper.task_new_list(request)
    task_delay_list = task_helper.task_delay_list(request)
    task_data = task_helper.task_table()
    project_data = project_helper.project_table()
    if request.user.is_superuser or request.user.is_admin:
        project_month = project_helper.project_month(request).count()
        project_shelve = project_helper.project_shelve(request)['count']
        project_examined = project_helper.project_examined(request).count()
        project_postpone = project_helper.project_postpone(request)['count']
        show_num = {'first':project_examined,'two':project_month,'three':project_postpone,'four':project_shelve}
    else:
        task_end = task_helper.task_new_day(request).count()
        task_all = task_helper.task_end_week(request).count()
        task_postpone = task_helper.task_postpone(request)['count']
        task_shelve = task_helper.task_shelve(request)['count']
        show_num = {'first': task_end, 'two': task_all, 'three': task_postpone, 'four': task_shelve}
    return render(request,'index.html',{'task_data':json.dumps(task_data),
                                        'project_data':json.dumps(project_data),
                                        'project_list':project_list,
                                        'task_new_list':task_new_list,
                                        'task_delay_list':task_delay_list,
                                        'show_num':show_num,
                                        })


def error_400(request):
    return render(request,'error/pages-error-400.html')

def error_403(request):
    return render(request,'error/pages-error-403.html')

def error_404(request):
    return render(request,'error/pages-error-404.html')

def error_500(request):
    return render(request,'error/pages-error-500.html')

def error_503(request):
    return render(request,'error/pages-error-503.html')

# @require_websocket
# def echo(request):
#     for message in request.websocket:
#         print(request.websocket.wait())
#         request.websocket.send(message)
#         time.sleep(5)
#         request.websocket.close()
#         print("aaaaa")
#         time.sleep(5)
#         print(request.websocket.wait())
