import datetime
import os
import json
from django.core import serializers
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from user.decorators import login_required, permission_required
from project import forms, models, tasks
from user.models import User, Csrf
from king_ad.views import obj
from project.helper import task_logs, project_logs, project_helper, task_helper, helper
from redmine2.settings import BASE_DIR


# Create your views here.

# 项目列表
@login_required(login_url='/login/')
@permission_required('project.view_project')
def project_obj(request):
    delay_form = forms.DelayForm()
    app_name = "project"
    table_name = "project"
    idss = []
    ids = []
    department = 0
    status = []
    if request.user.is_superuser == False and request.user.is_admin == False:
        project_users = models.ProjectUser.objects.filter(user=request.user)
        create_projects = models.Project.objects.filter(created_user=request.user)
        for create_project in create_projects:
            idss.append(create_project.id)
        for project_user in project_users:
            idss.append(project_user.project_id)
        idss = list(set(idss))
    if request.user.is_admin:
        project_users = models.ProjectUser.objects.filter(user=request.user)
        create_projects = models.Project.objects.filter(created_user=request.user)
        projects = models.Project.objects.filter(department=request.user.department)
        for project in projects:
            idss.append(project.id)
        for create_project in create_projects:
            idss.append(create_project.id)
        for project_user in project_users:
            idss.append(project_user.project_id)
        idss = list(set(idss))
    if request.user.is_superuser:
        projects = models.Project.objects.all()
        for project in projects:
            idss.append(project.id)
    if request.GET.get('sta') == '1':
        status = [1, 2, 5]
        request.GET._mutable = True
        request.GET["o"] = 'end_time'
    elif request.GET.get('sta') == '0':
        status = [0]
    elif request.GET.get('sta') == '3':
        status = [3, 4]
    for idd in idss[:]:
        project = models.Project.objects.get(id=idd)
        if project.status in status:
            ids.append(idd)
    request.GET._mutable = True
    request.GET['sta'] = ''
    ids.append(0)
    admin_class, query_sets, filter_condtions, orderby_key = obj(request, app_name, table_name, ids, department)
    return render(request, 'project/project_objs.html', {'admin_class': admin_class,
                                                         'query_sets': query_sets,
                                                         'filter_condtions': filter_condtions,
                                                         'orderby_key': orderby_key,
                                                         'precious_orderby': request.GET.get("o", ''),
                                                         'search_text': request.GET.get('_q', ''),
                                                         'delay_form': delay_form,
                                                         'table_name': table_name})


# 项目总览
@login_required(login_url='/login/')
def project_index(request):
    project_execute = project_helper.project_execute(request)
    project_shelve = project_helper.project_shelve(request)
    project_pause = project_helper.project_pause(request)
    project_examined_user = project_helper.project_examined_user(request)
    projects = project_helper.projects(request).count()
    project_end = project_helper.project_end(request)
    show_num = {'first': project_execute, 'two': project_shelve, 'three': project_pause, 'four': project_examined_user,
                'five': projects, 'six': project_end}
    project_chartist = project_helper.project_chartist(request)
    return render(request, 'project/project_index.html',
                  {'show_num': show_num, 'project_chartist': json.dumps(project_chartist)})


# 新建项目
@login_required(login_url='/login/')
@permission_required('project.add_project', login_url='/404/')
def project_add(request, type):
    users = User.objects.all()
    project_form = forms.ProjectForm()
    project_user_form = forms.ProjectUserForm()
    errors = ""
    if request.method == "POST":
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            project_form = forms.ProjectForm(request.POST)
            if project_form.is_valid():
                project = project_form.save(commit=False)
                project.examined = 0
                node = models.FlowNode.objects.get(flow=request.POST.get('flow'), num=1)
                project.node = node
                if models.NodeNode.objects.filter(flow=node, num=1):
                    project.node_node = models.NodeNode.objects.get(flow=node, num=1)
                project.created_user = request.user
                project.save()
                project_id = models.Project.objects.get(project_name=request.POST.get('project_name'))
                models.Examine.objects.create(project=project_id, examine=0, created_user=request.user)
                project_logs.new_project(project_id)
                if request.POST.get('user'):
                    first = True
                    for user_id in request.POST.get('user').split(','):
                        user = User.objects.get(id=user_id)
                        models.ProjectUser.objects.create(project=project_id, user=user, is_host=first)
                        first = False
                    tasks.send_new_project.delay(project_id)
                if request.POST.get('file'):
                    for file_id in request.POST.getlist('file'):
                        file = models.File.objects.get(id=file_id)
                        file.project = project_id
                        file.existent = True
                        file.save()
                        models.ProjectFile.objects.create(project=project_id, file=file)
                    helper.file_del(request)
                if request.POST.get('name'):
                    for index, name in enumerate(request.POST.getlist('name')):
                        num = index + 1
                        project_node = models.ProjectNode(project=project_id, name=name)
                        project_node.order = num
                        project_node.time = request.POST.get('time' + str(num))
                        project_node.number = request.POST.get('number' + str(num))
                        project_node.unit = request.POST.get('unit' + str(num))
                        if request.POST.get('node_alert_time' + str(num)):
                            project_node.node_alert_time = request.POST.get('node_alert_time' + str(num))
                        if request.POST.get('node' + str(num)):
                            project_node.node = models.FlowNode.objects.get(id=request.POST.get('node' + str(num)))
                        if request.POST.get('node_node' + str(num)):
                            project_node.node_node = models.NodeNode.objects.get(
                                id=request.POST.get('node_node' + str(num)))
                        project_node.save()
                return redirect(reverse('project') + '?sta=0')
            else:
                errors = project_form.errors
    return render(request, 'project/project_add.html', {'project_form': project_form,
                                                        'project_user_form': project_user_form,
                                                        'errors': errors,
                                                        'users': users,
                                                        'type': type, })


# 编辑项目
@login_required(login_url='/login/')
@permission_required('project.change_project', login_url='/404/')
def project_edit(request, id):
    errors = ""
    users = User.objects.all()
    project = models.Project.objects.get(id=id)
    if project.tag == 0:
        typ = 'inside'
    else:
        typ = 'outside'
    project_user = models.ProjectUser.objects.filter(project=id)
    project_node = models.ProjectNode.objects.filter(project=id).order_by("order")
    nodes = models.FlowNode.objects.filter(flow=project.flow)
    project_file = models.ProjectFile.objects.filter(project=id).select_related('file')
    node_id = project.node
    project_user_form = forms.ProjectUserForm()
    if request.method == "POST":
        project_form = forms.ProjectForm(request.POST, instance=project)
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if project_form.is_valid():
                project_form.save()
                project_logs.edit_project(project_form.changed_data, project, request.user)
                if request.POST.get('user'):
                    for user_id in request.POST.get('user').split(','):
                        user = User.objects.get(id=user_id)
                        if not models.ProjectUser.objects.filter(project=project, user=user):
                            models.ProjectUser.objects.create(project=project, user=user, is_host=False)
                            project_user = models.ProjectUser.objects.get(project=project, user=user)
                            tasks.send_project_add_user.delay(project_user)
                    project_logs.add_user(request.POST.getlist('user'), request.user, project)
                if request.POST.get('file'):
                    for file_id in request.POST.getlist('file'):
                        file = models.File.objects.get(id=file_id)
                        file.project = project
                        file.existent = True
                        file.save()
                        project_logs.add_file(file, request.user, project)
                        models.ProjectFile.objects.create(project=project, file=file)
                    helper.file_del(request)
                if request.POST.get('name'):
                    for index, name in enumerate(request.POST.getlist('name')):
                        num = index + 1
                        if models.ProjectNode.objects.filter(project=id, name=name).count() != 0:
                            project_node = models.ProjectNode.objects.get(project=id, name=name)
                            if project_node.order != num:
                                project_node.order = num
                                project_node.save()
                        else:
                            project_node = models.ProjectNode(project=project, name=name)
                            project_node.order = num
                            project_node.time = request.POST.get('time' + str(num))
                            project_node.number = request.POST.get('number' + str(num))
                            project_node.unit = request.POST.get('unit' + str(num))
                            if request.POST.get('node_alert_time' + str(num)):
                                project_node.node_alert_time = request.POST.get('node_alert_time' + str(num))
                            if request.POST.get('node' + str(num)):
                                project_node.node = models.FlowNode.objects.get(id=request.POST.get('node' + str(num)))
                            if request.POST.get('node_node' + str(num)):
                                project_node.node_node = models.NodeNode.objects.get(
                                    id=request.POST.get('node_node' + str(num)))
                            project_node.save()
                            project_logs.add_node(project_node, request.user)
                return redirect(reverse('project') + '?sta=1')
            else:
                errors = project_form.errors
    else:
        project_form = forms.ProjectForm(instance=project)
    return render(request, 'project/project_add.html', {'project_form': project_form,
                                                        'project_user_form': project_user_form,
                                                        'project_node': project_node,
                                                        'nodes': nodes,
                                                        'node_id': node_id,
                                                        'users': users,
                                                        'project_user': project_user,
                                                        'tag': project.tag,
                                                        'errors': errors,
                                                        'project_file': project_file,
                                                        'type': typ,
                                                        'project': project})


@login_required(login_url='/login/')
def project_show(request, id):
    project = models.Project.objects.get(id=id)
    project_user = models.ProjectUser.objects.filter(project=project)
    project_file = models.ProjectFile.objects.filter(project=project).select_related('file')
    examine = models.Examine.objects.filter(project=project).order_by("-examine").first()
    host_user = models.ProjectUser.objects.get(project=project, is_host=True)
    project_nodes = models.ProjectNode.objects.filter(project=project).order_by("order")
    project_discusses = models.ProjectDiscuss.objects.filter(project=project)
    project_logss = models.ProjectLog.objects.filter(project=project).order_by('-created_time')
    files = models.File.objects.filter(project=project).order_by('-created_time')
    project_records = models.ProjectRecord.objects.filter(project=project).order_by('-time')
    if request.method == "POST":
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if request.POST.get('class') == 'flow':
                node = models.FlowNode.objects.get(id=request.POST.get('node'))
                if request.POST.get('node_node'):
                    node_node = models.NodeNode.objects.get(id=request.POST.get('node_node'))
                else:
                    node_node = None
                if project.node != node or project.node_node != node_node:
                    project.node_node = node_node
                    project.node = node
                    project.save()
                    project_logs.node_project(project, request.user)
                tasks.send_project_node.delay(project)
            elif request.POST.get('class') == 'restart':
                if request.POST.get('supension_time'):
                    project.status = 1
                    project.end_time = request.POST.get('end_time')
                    project.save()
                    for index, project_node_id in enumerate(request.POST.getlist('id')):
                        order = index + 1
                        project_node = models.ProjectNode.objects.get(id=project_node_id)
                        if request.POST.get('time'):
                            project_node.time = request.POST.getlist('time')[index]
                        if request.POST.get('node_alert_time' + str(order)):
                            project_node.node_alert_time = request.POST.get('node_alert_time' + str(order))
                        project_node.save()
                    project_logs.restart_project(project, request.user)
                else:
                    project.status = 0
                    project.start_time = request.POST.get('start_time')
                    project.end_time = request.POST.get('end_time')
                    project.save()
                    for index, project_node_id in enumerate(request.POST.getlist('id')):
                        order = index + 1
                        project_node = models.ProjectNode.objects.get(id=project_node_id)
                        if request.POST.get('time'):
                            project_node.time = request.POST.getlist('time')[index]
                        if request.POST.get('node_alert_time' + str(order)):
                            project_node.node_alert_time = request.POST.get('node_alert_time' + str(order))
                        project_node.save()
                    project_logs.restart_project(project, request.user)
            elif request.POST.get('class') == 'stop':
                project.status = 3
                project.save()
                project_logs.statu_project(project, request.user)
                tasks.send_project_status.delay(project)
            elif request.POST.get('class') == 'supend':
                project.status = 5
                project.supension_time = datetime.datetime.now()
                project.save()
                taskes = models.Task.objects.filter(project=project)
                for task in taskes:
                    task.status = 5
                    task.save()
                    task_logs.supend_project(task, request.user)
                    tasks.send_task_status.delay(task)
                project_logs.supend_project(project, request.user)
                tasks.send_project_status.delay(project)
            elif request.POST.get('discuss'):
                order = models.ProjectDiscuss.objects.filter(project=project).count() + 1
                discuss = request.POST.get('discuss')
                project_discuss = models.ProjectDiscuss.objects.create(project=project, discuss=discuss, order=order,
                                                                       created_user=request.user)
                if request.POST.get('file'):
                    for file_id in request.POST.getlist('file'):
                        file = models.File.objects.get(id=file_id)
                        file.project = project
                        file.project_discuss = project_discuss
                        file.existent = True
                        file.save()
                        models.ProjectDiscussFile.objects.create(project_discuss=project_discuss, file=file)
                    helper.file_del(request)
                tasks.send_project_discuss.delay(project_discuss)
            else:
                if request.POST.get('discuss'):
                    order = models.ProjectDiscuss.objects.filter(project=project).count() + 1
                    discuss = request.POST.get('discuss')
                    project_discuss = models.ProjectDiscuss.objects.create(project=project, discuss=discuss,
                                                                           order=order,
                                                                           created_user=request.user)
                    if request.POST.get('file'):
                        for file_id in request.POST.getlist('file'):
                            file = models.File.objects.get(id=file_id)
                            file.project = project
                            file.project_discuss = project_discuss
                            file.existent = True
                            file.save()
                            models.ProjectDiscussFile.objects.create(project_discuss=project_discuss, file=file)
                        helper.file_del(request)
                    tasks.send_project_discuss.delay(project_discuss)
                if request.POST.get('record'):
                    models.ProjectRecord.objects.create(project=project, record=request.POST.get('record'),
                                                        time=request.POST.get('record_time'), created_user=request.user)
            return HttpResponseRedirect(reverse('project_show', kwargs={'id': id}))
    return render(request, 'project/project_show.html', {'project': project, 'project_user': project_user,
                                                         'project_file': project_file, 'examine': examine,
                                                         'host_user': host_user, 'project_nodes': project_nodes,
                                                         'project_discusses': project_discusses,
                                                         'project_logs': project_logss, 'files': files,
                                                         'project_records': project_records})


# 项目节点文件上传
@login_required(login_url='/login/')
@csrf_exempt
def project_node_file(request):
    if request.is_ajax():
        if request.POST.get('file[]'):
            project_node = models.ProjectNode.objects.get(id=request.POST.get('project_node'))
            project = project_node.project
            for file_id in request.POST.getlist('file[]'):
                file = models.File.objects.get(id=file_id)
                file.project = project
                file.existent = True
                file.save()
                models.ProjectNodeFile.objects.create(project_node=project_node, file=file, project=project)
                project_logs.add_file(file, request.user, project_node.project)
            helper.file_del(request)
            return JsonResponse({"resole": 0})


# 项目页面动态数据接口
@login_required(login_url='/login/')
@csrf_exempt
def project_api(request):
    if request.is_ajax():
        if request.POST.get('name') == 'department':
            flow = models.ProjectFlow.objects.filter(department_id=request.POST.get('id'))
            project_type = models.ProjectType.objects.filter(department_id=request.POST.get('id'))
            type_json = serializers.serialize("json", project_type)
            flow_json = serializers.serialize("json", flow)
            return JsonResponse({"flow": flow_json, "type": type_json}, safe=False)
        elif request.POST.get('name') == 'flow':
            node = models.FlowNode.objects.filter(flow_id=request.POST.get('id'))
            node_json = serializers.serialize("json", node)
            return JsonResponse(node_json, safe=False)
        elif request.POST.get('name') == 'project_node':
            project_node = models.ProjectNode.objects.filter(project_id=request.POST.get('id')).order_by("order")
            project_node_json = serializers.serialize("json", project_node)
            return JsonResponse(project_node_json, safe=False)
        elif request.POST.get('name') == 'node':
            node = models.FlowNode.objects.filter(flow_id=request.POST.get('id'))
            node_json = serializers.serialize("json", node)
            return JsonResponse(node_json, safe=False)
        elif request.POST.get('name') == 'node_node':
            node_node = models.NodeNode.objects.filter(flow_id=request.POST.get('id'))
            node_node_json = serializers.serialize("json", node_node)
            return JsonResponse(node_node_json, safe=False)
        elif request.POST.get('name') == 'task_project':
            if request.user.is_superuser:
                projects = models.Project.objects.filter(status__in=[1, 2])
            elif request.user.is_admin:
                ids = [0]
                project_users = models.ProjectUser.objects.filter(user=request.user)
                department_projects = models.Project.objects.filter(department=request.user.department,
                                                                    status__in=[1, 2])
                for project in department_projects:
                    ids.append(project.id)
                for project_user in project_users:
                    ids.append(project_user.project_id)
                ids = list(set(ids))
                projects = models.Project.objects.filter(id__in=ids, status__in=[1, 2])
            else:
                ids = [0]
                project_users = models.ProjectUser.objects.filter(user=request.user)
                for project_user in project_users:
                    ids.append(project_user.project_id)
                projects = models.Project.objects.filter(id__in=ids, status__in=[1, 2])
            projects_json = serializers.serialize("json", projects)
            return JsonResponse(projects_json, safe=False)
        else:
            return JsonResponse({"resole": 0})


# 项目流程列表
@login_required(login_url='/login/')
@permission_required('project.view_projectflow', login_url='/404/')
def flow_index(request):
    app_name = "project"
    table_name = "projectflow"
    ids = []
    depertment = 0
    if request.user.is_admin:
        depertment = request.user.department_id
    admin_class, query_sets, filter_condtions, orderby_key = obj(request, app_name, table_name, ids, depertment)
    return render(request, 'project/project_objs.html', {'admin_class': admin_class,
                                                         'query_sets': query_sets,
                                                         'filter_condtions': filter_condtions,
                                                         'orderby_key': orderby_key,
                                                         'precious_orderby': request.GET.get("o", ''),
                                                         'search_text': request.GET.get('_q', '')})


# 项目流程新建
@login_required(login_url='/login/')
@permission_required('project.add_projectflow', login_url='/404/')
def flow_add(request):
    errors = ""
    flow_from = forms.ProjectFlowForm()
    if request.method == "POST":
        flow_from = forms.ProjectFlowForm(request.POST)
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if flow_from.is_valid():
                flow_from.save()
                flow_id = models.ProjectFlow.objects.get(flow_name=request.POST.get('flow_name'))
                if request.POST.get('node_name'):
                    for index, node_name in enumerate(request.POST.getlist('node_name')):
                        num = index + 1
                        type_name = 'name' + str(index)
                        models.FlowNode.objects.create(node_name=node_name, flow=flow_id, num=num)
                        flow_node = models.FlowNode.objects.get(flow=flow_id, node_name=node_name)
                        if request.POST.get(type_name):
                            for k, name in enumerate(request.POST.getlist(type_name)):
                                node_num = k + 1
                                models.NodeNode.objects.create(name=name, flow=flow_node, num=node_num)
                    return redirect(reverse('flow'))
            else:
                errors = flow_from.errors
    return render(request, 'project/flow_change.html', {'flow_from': flow_from, 'errors': errors})


# 编辑项目流程
@login_required(login_url='/login/')
@permission_required('project.change_projectflow', login_url='/404/')
def flow_edit(request, id):
    flow = models.ProjectFlow.objects.get(id=id)
    nodes = models.FlowNode.objects.filter(flow=id)
    flow_from = forms.ProjectFlowForm(instance=flow)
    node_nodes = {}
    for no in nodes:
        node_nodes[no] = models.NodeNode.objects.filter(flow=no)
    if request.method == "POST":
        flow_from = forms.ProjectFlowForm(request.POST, instance=flow)
        if flow_from.is_valid():
            flow_from.save()
            return redirect(reverse('flow'))
    return render(request, 'project/flow_change.html',
                  {'flow_from': flow_from, 'node': nodes, 'node_node': node_nodes, 'flow': flow})


# 任务列表
@login_required(login_url='/login/')
@permission_required('project.view_task', login_url='/404/')
def task_obj(request):
    delay_form = forms.DelayForm()
    app_name = "project"
    table_name = "task"
    ids = []
    idss = []
    department = 0
    status = []
    if request.user.is_superuser == False and request.user.is_admin == False:
        task_users = models.TaskUser.objects.filter(user=request.user)
        create_tasks = models.Task.objects.filter(created_user=request.user)
        for create_task in create_tasks:
            idss.append(create_task.id)
        for task_user in task_users:
            idss.append(task_user.task_id)
        idss = list(set(idss))
    if request.user.is_admin:
        task_users = models.TaskUser.objects.filter(user=request.user)
        create_tasks = models.Task.objects.filter(created_user=request.user)
        for create_task in create_tasks:
            idss.append(create_task.id)
        for task_user in task_users:
            idss.append(task_user.task_id)
        department_id = request.user.department_id
        projects = models.Project.objects.filter(department=department_id)
        for project in projects:
            taskes = models.Task.objects.filter(project=project)
            for task in taskes:
                idss.append(task.id)
        idss = list(set(idss))
    if request.user.is_superuser:
        taskes = models.Task.objects.all()
        for task in taskes:
            idss.append(task.id)
    if request.GET.get('sta') == '1':
        status = [1, 2, 5]
        request.GET._mutable = True
        request.GET["o"] = 'end_time'
    elif request.GET.get('sta') == '0':
        status = [0]
    elif request.GET.get('sta') == '3':
        status = [3, 4]
    for idd in idss[:]:
        task = models.Task.objects.get(id=idd)
        if task.status in status:
            ids.append(idd)
    request.GET._mutable = True
    request.GET['sta'] = ''
    ids.append(0)
    admin_class, query_sets, filter_condtions, orderby_key = obj(request, app_name, table_name, ids, department)
    return render(request, 'project/project_objs.html', {'admin_class': admin_class,
                                                         'query_sets': query_sets,
                                                         'filter_condtions': filter_condtions,
                                                         'orderby_key': orderby_key,
                                                         'precious_orderby': request.GET.get("o", ''),
                                                         'search_text': request.GET.get('_q', ''),
                                                         'delay_form': delay_form,
                                                         'table_name': table_name})


@login_required(login_url='/login/')
def task_index(request):
    task_execute = task_helper.task_execute(request)
    task_shelve = task_helper.task_shelve(request)
    task_pause = task_helper.task_pause(request)
    task_examined_user = task_helper.task_examined_user(request)
    taskes = task_helper.taskes(request).count()
    task_end = task_helper.task_end(request)
    show_num = {'first': task_execute, 'two': task_shelve, 'three': task_pause, 'four': task_examined_user,
                'five': taskes, 'six': task_end}
    task_chartist = task_helper.task_chartist(request)
    return render(request, 'project/task_index.html',
                  {'task_chartist': json.dumps(task_chartist), 'show_num': show_num})


@login_required(login_url='/login/')
def task_show(request, id):
    task = models.Task.objects.get(id=id)
    task_user = models.TaskUser.objects.filter(task=task)
    task_file = models.TaskFile.objects.filter(task=task).select_related('file')
    task_discusses = models.TaskDiscuss.objects.filter(task=task)
    host_user = task_user.filter(is_host=True)
    task_logss = models.TaskLog.objects.filter(task=task).order_by('-created_time')
    files = models.File.objects.filter(task=task).order_by('-created_time')
    ids = []
    for task_use in task_user:
        ids.append(task_use.user_id)
    users = User.objects.filter(id__in=ids)
    if request.method == 'POST':
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if request.POST.get('discuss'):
                order = models.TaskDiscuss.objects.filter(task=task).count() + 1
                discuss = request.POST.get('discuss')
                task_discuss = models.TaskDiscuss.objects.create(task=task, discuss=discuss, order=order,
                                                                 created_user=request.user)
                if request.POST.get('file'):
                    for file_id in request.POST.getlist('file'):
                        file = models.File.objects.get(id=file_id)
                        if task.project:
                            file.project = task.project
                        file.task = task
                        file.task_discuss = task_discuss
                        file.existent = True
                        file.save()
                        models.TaskDiscussFile.objects.create(task_discuss=task_discuss, file=file)
                    helper.file_del(request)
                tasks.send_task_discuss.delay(task_discuss)
            else:
                if request.POST.get('class') == 'restart':
                    task.end_time = request.POST.get('end_time')
                    task.status = 1
                    task.save()
                    task_logs.restart_task(task, request.user)
                    tasks.send_task5.delay(task)
                else:
                    task.status = 5
                    task.save()
                    task_logs.supend_project(task, request.user)
                    tasks.send_task_status.delay(task)
            return HttpResponseRedirect(reverse('task_show', kwargs={'id': id}))
    return render(request, 'project/task_show.html', {'task': task, 'task_user': task_user, 'task_file': task_file,
                                                      'users': users, 'task_discusses': task_discusses,
                                                      'host_user': host_user, 'task_logs': task_logss,
                                                      'files': files})


# 新建任务
@login_required(login_url='/login/')
@permission_required('project.add_task', login_url='/404/')
def task_add(request):
    errors = ""
    task_form = forms.TaskForm()
    task_user_form = forms.TaskUserForm()
    if request.method == "POST":
        task_form = forms.TaskForm(request.POST)
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.created_user = request.user
                task.save()
                task_id = models.Task.objects.get(name=request.POST['name'])
                task_logs.new_task(task)
                if request.POST.get('user'):
                    first = True
                    for user_id in request.POST.get('user').split(','):
                        user = User.objects.get(id=user_id)
                        models.TaskUser.objects.create(task=task_id, user=user, is_host=first)
                        first = False
                    tasks.send_new_task.delay(task_id)
                if request.POST.get('file'):
                    for file_id in request.POST.getlist('file'):
                        file = models.File.objects.get(id=file_id)
                        if request.POST.get('project'):
                            project = models.Project.objects.get(id=request.POST.get('project'))
                            file.project = project
                        file.task = task_id
                        file.existent = True
                        file.save()
                        models.TaskFile.objects.create(task=task_id, file=file)
                    helper.file_del(request)
                return redirect(reverse('task') + '?sta=0')
            else:
                errors = task_form.errors
    return render(request, 'project/task_change.html',
                  {'task_form': task_form, 'task_user_form': task_user_form, 'errors': errors})


# 任务执行
@login_required(login_url='/login/')
@csrf_exempt
def task_status(request):
    if request.is_ajax():
        print(request.POST)
        task = models.Task.objects.get(id=request.POST.get('id'))
        if task.project_id:
            project = models.Project.objects.get(id=task.project_id)
            if project.status == 0:
                return JsonResponse({"resole": 0})
            elif project.status == 3:
                return JsonResponse({"resole": 4})
            else:
                if task.status == 0:
                    task.status = 1
                else:
                    task.status = 3
                task.save()
                task_logs.status_task(task, request.user)
                tasks.send_task_status.delay(task)
                return JsonResponse({"resole": 1})
        else:
            if task.status == 0:
                task.status = 1
            else:
                task.status = 3
            task.save()
            task_logs.status_task(task, request.user)
            tasks.send_task_status.delay(task)
            return JsonResponse({"resole": 1})


# 文件上传
@login_required(login_url='/login/')
@csrf_exempt
def upload(request):
    if request.is_ajax():
        if request.FILES.get('file'):
            file_obj = request.FILES.get('file')
            name, type = os.path.splitext(file_obj.name)
            try:
                file = models.File.objects.create(name=file_obj.name, file=file_obj, created_user=request.user,
                                                  postfix=type)
                return JsonResponse({"resole": file.id, "file": file_obj.name})
            except Exception:
                return JsonResponse({"resole": 0, "file": file_obj.name})


# 编辑任务
@login_required(login_url='/login/')
@permission_required('project.change_task', login_url='/404/')
def task_edit(request, id):
    task = models.Task.objects.get(id=id)
    task_users = models.TaskUser.objects.filter(task=id)
    task_user_form = forms.TaskUserForm()
    task_file = models.TaskFile.objects.filter(task=id).select_related('file')
    if request.method == "POST":
        task_form = forms.TaskForm(request.POST, instance=task)
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if task_form.is_valid():
                task_form.save()
                task_logs.edit_task(task_form.changed_data, request.user, task)
            if request.POST.get('user'):
                for user_id in request.POST.get('user').split(','):
                    user = User.objects.get(id=user_id)
                    models.TaskUser.objects.create(task=task, user=user, is_host=False)
                    task_user = models.TaskUser.objects.get(task=task, user=user)
                    tasks.send_task_add_user.delay(task_user)
                task_logs.add_user(request.POST.getlist('user'), request.user, task)
            if request.POST.get('file'):
                for file_id in request.POST.getlist('file'):
                    file = models.File.objects.get(id=file_id)
                    if request.POST.get('project'):
                        project = models.Project.objects.get(id=request.POST.get('project'))
                        file.project = project
                    file.task = task
                    file.existent = True
                    file.save()
                    task_logs.add_file(file, request.user, task)
                    models.TaskFile.objects.create(task=task, file=file)
                helper.file_del(request)
            return redirect(reverse('task') + '?sta=1')
    else:
        task_form = forms.TaskForm(instance=task)
    return render(request, 'project/task_change.html', {'task_form': task_form, 'task_users': task_users,
                                                        'task_user_form': task_user_form,
                                                        'task_file': task_file, 'task': task})


# 延期申请列表
@login_required(login_url='/login/')
@permission_required('project.view_delay', login_url='/404/')
def delay_obj(request):
    app_name = 'project'
    table_name = 'delay'
    ids = []
    depertment = 0
    if request.user.is_admin:
        ids.append(0)
        depertment_id = request.user.department
        projects = models.Project.objects.filter(department=depertment_id).exclude(status=4)
        for project in projects:
            delays = models.Delay.objects.filter(project=project)
            for delay in delays:
                ids.append(delay.id)
    admin_class, query_sets, filter_condtions, orderby_key = obj(request, app_name, table_name, ids, depertment)
    return render(request, 'project/project_objs.html', {'admin_class': admin_class,
                                                         'query_sets': query_sets,
                                                         'filter_condtions': filter_condtions,
                                                         'orderby_key': orderby_key,
                                                         'precious_orderby': request.GET.get("o", ''),
                                                         'search_text': request.GET.get('_q', ''),
                                                         'table_name': table_name})


# 项目延期申请
@login_required(login_url='/login/')
@csrf_exempt
def delay_add(request):
    if request.is_ajax():
        typ = request.POST.get('type')
        if typ == '任务延期':
            task = models.Task.objects.get(id=request.POST.get('task'))
            if task.project:
                project = task.project
                delay = models.Delay.objects.create(type=typ, project=project, task=task,
                                                    reason=request.POST.get('reason'),
                                                    time=request.POST.get('time'),
                                                    created_user=request.user)
                task_logs.delay_task(delay)
                tasks.send_delay.delay(delay)
                task.delay_status = 1
                task.save()
                return JsonResponse({"resole": task.delay_status, "id": request.POST.get('task')})
            else:
                delay = models.Delay.objects.create(type=typ, task=task,
                                                    reason=request.POST.get('reason'),
                                                    time=request.POST.get('time'),
                                                    created_user=request.user)
                task_logs.delay_task(delay)
                tasks.send_delay.delay(delay)
                task.delay_status = 1
                task.save()
            return JsonResponse({"resole": task.delay_status, "id": request.POST.get('task')})
        elif typ == '项目延期':
            project = models.Project.objects.get(id=request.POST.get('project'))
            delay = models.Delay.objects.create(type=typ, project=project,
                                                reason=request.POST.get('reason'),
                                                time=request.POST.get('time'),
                                                created_user=request.user)
            project_logs.delay_project(delay)
            tasks.send_delay.delay(delay)
            project.delay_status = 1
            project.save()
            return JsonResponse({"resole": project.delay_status, "id": request.POST.get('project')})
        elif typ == '节点延期':
            project = models.Project.objects.get(id=request.POST.get('project'))
            project_node = models.ProjectNode.objects.get(id=request.POST.get('project_node'))
            delay = models.Delay.objects.create(type=typ, project=project, project_node=project_node,
                                                reason=request.POST.get('reason'),
                                                time=request.POST.get('time'),
                                                created_user=request.user,
                                                spare=request.POST.get('spare'))
            project_logs.node_delay_project(delay)
            tasks.send_delay.delay(delay)
            return JsonResponse({"resole": 0})
        return JsonResponse({"resole": 0})


# 延期申请审批
@login_required(login_url='/login/')
@permission_required('project.change_delay', login_url='/404/')
def delay_edit(request, id):
    delay = models.Delay.objects.get(id=id)
    project = delay.project
    task = delay.task
    project_node = delay.project_node
    project_user = models.ProjectUser.objects.filter(project=delay.project_id)
    project_file = models.ProjectFile.objects.filter(project=delay.project_id)
    task_user = models.TaskUser.objects.filter(task=delay.task_id)
    task_file = models.TaskFile.objects.filter(task=delay.task_id)
    errors = ""
    if request.method == 'POST':
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if request.user.is_admin or request.user.is_superuser:
                if request.POST['is_pass'] == '1':
                    delay.user = request.user
                    delay.is_pass = True
                    delay.save()
                    if delay.type == '项目延期':
                        project_logs.delay_pass(delay)
                        project.end_time = delay.time
                        project.delay_status = 2
                        project.save()
                    elif delay.type == '节点延期':
                        project_logs.node_delay_pass(delay)
                        old_time = delay.project_node.time
                        new_time = delay.time
                        if delay.spare == 'true':
                            i = delay.project_node.order
                            project_nodes = models.ProjectNode.objects.filter(project=project, order__gte=i)
                            if new_time > old_time:
                                time_val = (new_time - old_time).seconds
                                project_end_time = project.end_time + datetime.timedelta(seconds=time_val)
                                project.end_time = project_end_time
                                project.save()
                                for node in project_nodes:
                                    node_time = node.time + datetime.timedelta(seconds=time_val)
                                    node.time = node_time
                                    if node.node_alert_time:
                                        node.node_alert_time = node.node_alert_time + datetime.timedelta(
                                            seconds=time_val)
                                    node.save()
                            else:
                                time_val = (old_time - new_time).seconds
                                project_end_time = project.end_time - datetime.timedelta(seconds=time_val)
                                project.end_time = project_end_time
                                project.save()
                                for node in project_nodes:
                                    node_time = node.time - datetime.timedelta(seconds=time_val)
                                    node.time = node_time
                                    if node.node_alert_time:
                                        node.node_alert_time = node.node_alert_time - datetime.timedelta(
                                            seconds=time_val)
                                    node.save()
                        else:
                            if new_time > old_time:
                                time_val = (new_time - old_time).seconds
                                if project_node.node_alert_time:
                                    project_node.node_alert_time = project_node.node_alert_time + datetime.timedelta(
                                        seconds=time_val)
                            else:
                                time_val = (old_time - new_time).seconds
                                if project_node.node_alert_time:
                                    project_node.node_alert_time = project_node.node_alert_time - datetime.timedelta(
                                        seconds=time_val)
                            project_node.time = delay.time
                            project_node.save()
                    elif delay.type == '任务延期':
                        task_logs.delay_pass(delay)
                        old_time = task.end_time
                        new_time = delay.time
                        if new_time > old_time:
                            time_val = (new_time - old_time).seconds
                            if task.alert_time:
                                task.alert_time = task.alert_time + datetime.timedelta(seconds=time_val)
                        else:
                            time_val = (old_time - new_time).seconds
                            if task.alert_time:
                                task.alert_time = task.alert_time - datetime.timedelta(seconds=time_val)
                        task.end_time = delay.time
                        task.delay_status = 2
                        task.save()
                elif request.POST['is_pass'] == '0':
                    delay.is_pass = False
                    delay.user = request.user
                    delay.description = request.POST['description']
                    delay.save()
                    if delay.type == '项目延期':
                        project_logs.delay_pass(delay)
                        project.delay_status = 3
                        project.save()
                    elif delay.type == '任务延期':
                        task_logs.delay_pass(delay)
                        task.delay_status = 3
                        task.save()
                    elif delay.type == '节点延期':
                        project_logs.node_delay_pass(delay)
                tasks.send_delay.delay(delay)
                project_node = delay.project_node
            else:
                errors = "对不起！您没有权限！"
    return render(request, 'project/delay_edit.html', {'delay': delay, 'project': project, 'task': task,
                                                       'project_node': project_node, 'errors': errors,
                                                       'project_user': project_user, 'project_file': project_file,
                                                       'task_user': task_user, 'task_file': task_file})


# 项目审核列表
@login_required(login_url='/login/')
@permission_required('project.view_examine', login_url='/404/')
def examine_obj(request):
    app_name = 'project'
    table_name = 'examine'
    ids = []
    depertment = 0
    projects = ''
    request.GET._mutable = True
    if request.user.is_superuser:
        request.GET["examine"] = '1'
        projects = models.Project.objects.all().exclude(status=4)
    elif request.user.is_admin:
        request.GET["examine"] = '0'
        ids.append(0)
        depertment_id = request.user.department
        projects = models.Project.objects.filter(department=depertment_id).exclude(status=4)
    for project in projects:
        examines = models.Examine.objects.filter(project=project)
        for examine in examines:
            ids.append(examine.id)
    admin_class, query_sets, filter_condtions, orderby_key = obj(request, app_name, table_name, ids, depertment)
    return render(request, 'project/project_objs.html', {'admin_class': admin_class,
                                                         'query_sets': query_sets,
                                                         'filter_condtions': filter_condtions,
                                                         'orderby_key': orderby_key,
                                                         'precious_orderby': request.GET.get("o", ''),
                                                         'search_text': request.GET.get('_q', ''),
                                                         'table_name': table_name})


# 项目审核审批
@login_required(login_url='/login/')
@permission_required('project.change_examine', login_url='/404/')
def examine_edit(request, id):
    examine = models.Examine.objects.get(id=id)
    project = examine.project
    project_user = models.ProjectUser.objects.filter(project=examine.project_id)
    project_file = models.ProjectFile.objects.filter(project=examine.project_id)
    errors = ""
    if request.method == "POST":
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if examine.examine == 0:
                if request.user.is_admin:
                    if request.POST['is_pass'] == '1':
                        examine.is_pass = True
                        examine.examine_user = request.user
                        examine.save()
                        project = models.Project.objects.get(id=examine.project_id)
                        project.examined = 1
                        project.save()
                        models.Examine.objects.create(project=examine.project, examine=1, created_user=request.user)
                    elif request.POST['is_pass'] == '0':
                        examine.is_pass = False
                        examine.examine_user = request.user
                        examine.description = request.POST['description']
                        examine.save()
                        project = models.Project.objects.get(id=examine.project_id)
                        project.examined = 3
                        project.status = 3
                        project.save()
                    project_logs.examine_project(examine)
                    tasks.send_admin_project.delay(examine)
                    return redirect(reverse('examine') + '?examine=0')
                elif request.user.is_superuser:
                    errors = "请等待部门经理审批通过"
                else:
                    errors = "对不起！您没有权限！"
            elif examine.examine == 1:
                if request.user.is_superuser:
                    if request.POST['is_pass'] == '1':
                        examine.is_pass = True
                        examine.examine_user = request.user
                        examine.save()
                        project = models.Project.objects.get(id=examine.project_id)
                        project.examined = 2
                        project.status = 1
                        project.save()
                    elif request.POST['is_pass'] == '0':
                        examine.is_pass = False
                        examine.examine_user = request.user
                        examine.description = request.POST['description']
                        examine.save()
                        project = models.Project.objects.get(id=examine.project_id)
                        project.examined = 3
                        project.status = 3
                        project.save()
                    project_logs.examine_project(examine)
                    tasks.send_superuser_project.delay(examine)
                    return redirect(reverse('examine') + '?examine=1')
                else:
                    errors = "对不起！您没有权限！"
    return render(request, "project/examine_change.html", {"examine": examine, 'errors': errors,
                                                           'project': project,
                                                           'project_user': project_user,
                                                           'project_file': project_file})


# 贡献列表
@login_required(login_url='/login/')
@permission_required('project.view_contribution', login_url='/404/')
def contribution_obj(request):
    app_name = 'project'
    table_name = 'contribution'
    admin_class, query_sets, filter_condtions, orderby_key = obj(request, app_name, table_name)
    return render(request, 'project/project_objs.html', {'admin_class': admin_class,
                                                         'query_sets': query_sets,
                                                         'filter_condtions': filter_condtions,
                                                         'orderby_key': orderby_key,
                                                         'precious_orderby': request.GET.get("o", ''),
                                                         'search_text': request.GET.get('_q', '')})


# 新建贡献
@login_required(login_url='/login/')
@permission_required('project.add_contribution', login_url='/404/')
def contribution_add(request):
    errors = ""
    contribution_form = forms.ContributionForm()
    if request.method == "POST":
        contribution_form = forms.ContributionForm(request.POST)
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if contribution_form.is_valid():
                contribution = contribution_form.save(commit=False)
                contribution.created_user = request.user
                contribution.save()
                contributions = models.Contribution.objects.get(name=request.POST.get('name'))
                for use in request.POST.get('user').split(','):
                    user = User.objects.get(id=use)
                    contributions.user.add(user)
                return redirect(request.path.replace('/add/', "/"))
            else:
                errors = contribution_form.errors
    return render(request, 'project/contribution_add.html',
                  {'contribution_form': contribution_form, 'errors': errors})


# 编辑贡献
@login_required(login_url='/login/')
@permission_required('project.change_contribution', login_url='/404/')
def contribution_edit(request, id):
    errors = ""
    contribution = models.Contribution.objects.get(id=id)
    contribution_form = forms.ContributionForm(instance=contribution)
    if request.method == "POST":
        contribution_form = forms.ContributionForm(request.POST, instance=contribution)
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if contribution_form.is_valid():
                contribution.save()
                if request.POST.get('user'):
                    for use in request.POST.get('user').split(','):
                        user = User.objects.get(id=use)
                        contribution.user.add(user)
                return redirect(request.path.replace('/change/', "/"))
            else:
                errors = contribution_form.errors
    return render(request, 'project/contribution_add.html',
                  {'contribution_form': contribution_form, 'errors': errors, 'contribution': contribution})


# 查看贡献
@login_required(login_url='/login/')
@permission_required('project.view_contribution', login_url='/404/')
def contribution_show(request, id):
    contribution = models.Contribution.objects.get(id=id)
    return render(request, 'project/contribution_show.html', {'contribution': contribution})


@login_required(login_url='/login/')
def notice(request):
    if request.method == 'POST':
        if request.POST.get('notice'):
            for notice_id in request.POST.getlist('notice'):
                notice = models.Notice.objects.get(id=notice_id)
                notice.active = False
                notice.save()
    notices = models.Notice.objects.filter(to_user=request.user, active=True).order_by('-created_time')
    if request.GET.get('type'):
        notices = notices.filter(type=request.GET.get('type'))
    filter_conditions = {}
    paginator = Paginator(notices, 10)
    page = request.GET.get('page')
    try:
        query_sets = paginator.page(page)
    except PageNotAnInteger:
        query_sets = paginator.page(1)
    except EmptyPage:
        query_sets = paginator.page(paginator.num_pages)
    return render(request, 'notice.html', {'query_sets': query_sets,
                                           'filter_condtions': filter_conditions, })


@login_required(login_url='/login/')
@csrf_exempt
def new_notice(request):
    notices = models.Notice.objects.filter(read="0", to_user=request.user)
    if request.method == 'GET':
        if notices.count() == 0:
            return JsonResponse({"resole": 1})
        else:
            return JsonResponse({"resole": 0})
    if request.is_ajax():
        notices.update(read="1")
        return JsonResponse({"resole": 1})


@login_required(login_url='/login/')
def file_project(request):
    app_name = 'project'
    table_name = 'project'
    admin_class, query_sets, filter_condtions, orderby_key = obj(request, app_name, table_name)
    return render(request, 'file_project.html', {'admin_class': admin_class,
                                                 'query_sets': query_sets,
                                                 'filter_condtions': filter_condtions,
                                                 'orderby_key': orderby_key,
                                                 'precious_orderby': request.GET.get("o", ''),
                                                 'search_text': request.GET.get('_q', '')})


@login_required(login_url='/login/')
def file_obj(request):
    app_name = 'project'
    table_name = 'file'
    request.GET._mutable = True
    request.GET["existent"] = '1'
    admin_class, query_sets, filter_condtions, orderby_key = obj(request, app_name, table_name)
    return render(request, 'file_objs.html', {'admin_class': admin_class,
                                              'query_sets': query_sets,
                                              'filter_condtions': filter_condtions,
                                              'orderby_key': orderby_key,
                                              'precious_orderby': request.GET.get("o", ''),
                                              'search_text': request.GET.get('_q', '')})


import uuid


@csrf_exempt
def image(request):
    if request.method == 'POST':
        item = {}
        file = request.FILES.get('file')
        ext_name = file.name.rfind('.')
        localtime = datetime.datetime.now().strftime('%Y/%m/%d')
        file_dirs = os.path.join(BASE_DIR, 'media', 'image', localtime)
        path = os.path.join('media/image/', localtime)
        if not os.path.exists(path):
            os.makedirs(file_dirs)
        file_name = str(uuid.uuid1()) + file.name[ext_name:]
        file_path = os.path.join(path, file_name)
        try:
            with open(file_path, 'wb') as f:
                for temp in file.chunks():
                    f.write(temp)
            item['code'] = 0
            item['msg'] = '上传失败'
            item['data'] = {'src': '/' + file_path}
        except:
            item['code'] = 1
            item['msg'] = '上传失败'
            item['data'] = {'src': '/' + file_path}
        return JsonResponse(item)
