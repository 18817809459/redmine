from __future__ import absolute_import
from celery import shared_task, task
from user.models import User
from project import models
from django.core.mail import send_mail
import datetime
from project.helper import project_logs, task_logs

email = 'yingxiaotai@izhihuo.com'


@shared_task
def send_user(user, password):
    ele_user = "{name},欢迎您，加入营销台！".format(name=user.first_name)
    models.Notice.objects.create(notice=ele_user, to_user=user, type=3)
    try:
        ele = "{name},欢迎您，加入营销台！你的密码为：{password}。你可以使用企业邮箱和手机号进行登陆。".format(name=user.first_name, password=password)
        send_mail("欢迎加入营销台", ele, email, [user.email], fail_silently=False)
    except Exception:
        models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)


@shared_task
def send_new_project(project):
    user_ele = ""
    create_user = project.created_user
    department = create_user.department
    to_users = models.ProjectUser.objects.filter(project=project)
    for user in to_users:
        user_ele += "%s，" % user.user.first_name
    admin = User.objects.filter(department=project.department, is_admin=True)
    superuser = User.objects.filter(is_superuser=True)
    for user in to_users:
        ele_user = "{department}-{create_user}创建了{tag}项目-{name}，项目托付人为{user_ele}。".format(
            create_user=create_user, tag=project.get_tag_display(), name=project.project_name, user_ele=user_ele,
            department=department
        )
        models.Notice.objects.create(notice=ele_user, to_user=user.user, type=0)
        try:
            send_mail("新建项目提醒", ele_user, email, [user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
    for user in admin:
        ele_user = "{department}-{create_user}创建了{tag}项目-{name}，{add}项目托付人为{user}。".format(
            create_user=create_user, tag=project.get_tag_display(), name=project.project_name, user=user_ele,
            add="需进行审批，", department=department
        )
        models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
        try:
            send_mail("新建项目提醒", ele_user, email, [user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)
    for user in superuser:
        ele_user = "{department}-{create_user}创建了{tag}项目-{name}，项目托付人为{user}。".format(
            create_user=create_user, tag=project.get_tag_display(), name=project.project_name, user=user_ele,
            department=department
        )
        models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
        try:
            send_mail("新建项目提醒", ele_user, email, [user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)


@shared_task
def send_project_node(project):
    to_users = models.ProjectUser.objects.filter(project=project)
    superuser = User.objects.filter(is_superuser=True)
    ele_user = "{tag}项目-{name}，项目节点变更为{node}-->{node_node}。".format(
        node=project.node, tag=project.get_tag_display(), name=project.project_name, node_node=project.node_node)
    for user in to_users:
        models.Notice.objects.create(notice=ele_user, to_user=user.user, type=0)
        try:
            send_mail("项目环节变更提醒", ele_user, email, [user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
    for user in superuser:
        models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
        try:
            send_mail("项目环节变更提醒", ele_user, email, [user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)


@shared_task
def send_project_status(project):
    user_ele = ""
    to_users = models.ProjectUser.objects.filter(project=project)
    for user in to_users:
        user_ele += "%s，" % user.user.first_name
    superuser = User.objects.filter(is_superuser=True)
    if project.status == 3:
        ele_user = "{tag}项目-{name}已结束，项目托付人为{user_ele}。".format(
            tag=project.get_tag_display(), name=project.project_name, user_ele=user_ele)
        for user in to_users:
            models.Notice.objects.create(notice=ele_user, to_user=user.user, type=0)
            try:
                send_mail("项目结束提醒", ele_user, email, [user.user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
        for user in superuser:
            models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
            try:
                send_mail("项目结束提醒", ele_user, email, [user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)
    elif project.status == 5:
        ele_user = "{tag}项目-{name}已暂停，项目托付人为{user_ele}。".format(
            tag=project.get_tag_display(), name=project.project_name, user_ele=user_ele)
        for user in to_users:
            models.Notice.objects.create(notice=ele_user, to_user=user.user, type=0)
            try:
                send_mail("项目暂停提醒", ele_user, email, [user.user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
        for user in superuser:
            models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
            try:
                send_mail("项目暂停提醒", ele_user, email, [user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)


@shared_task
def send_admin_project(examine):
    user_ele = ""
    project = examine.project
    examine_user = examine.examine_user
    department = examine_user.department
    to_users = models.ProjectUser.objects.filter(project=project)
    for user in to_users:
        user_ele += "%s，" % user.user.first_name
    superuser = User.objects.filter(is_superuser=True)
    if examine.is_pass:
        add = "通过"
    else:
        add = "拒绝"
    for user in to_users:
        ele_user = "{department}-{examine_user}{add}了{tag}项目-{name}的审批申请。".format(
            examine_user=examine_user, tag=project.get_tag_display(), name=project.project_name, user=user_ele,
            department=department, add=add
        )
        models.Notice.objects.create(notice=ele_user, to_user=user.user, type=0)
        try:
            send_mail("项目审批提醒（经理）", ele_user, email, [user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
    for user in superuser:
        ele_user = "{department}-{examine_user}通过了{tag}项目-{name}的审批申请。".format(
            examine_user=examine_user, tag=project.get_tag_display(), name=project.project_name, user=user_ele,
            department=department, add=add
        )
        models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
        try:
            send_mail("项目审批提醒（经理）", ele_user, email, [user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)


@shared_task
def send_superuser_project(examine):
    user_ele = ""
    project = examine.project
    department = project.department
    examine_user = examine.examine_user
    to_users = models.ProjectUser.objects.filter(project=project)
    for user in to_users:
        user_ele += "%s，" % user.user.first_name
    admin = User.objects.filter(department=department, is_admin=True)
    if examine.is_pass:
        add = "通过"
        ele = "管理员审批通过，{tag}项目-{name}，状态变更为执行中。".format(
            tag=project.get_tag_display(), name=project.project_name)
        for user in to_users:

            models.Notice.objects.create(notice=ele, to_user=user.user, type=0)
            try:
                send_mail("项目状态变更提醒", ele, email, [user.user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
        for user in admin:
            models.Notice.objects.create(notice=ele, to_user=user, type=0)
            try:
                send_mail("项目状态变更提醒", ele, email, [user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)
    else:
        add = "拒绝"
    for user in to_users:
        ele_user = "管理员-{examine_user}{add}了{tag}项目-{name}的审批申请。".format(
            examine_user=examine_user, tag=project.get_tag_display(), name=project.project_name, user=user_ele,
            add=add
        )
        models.Notice.objects.create(notice=ele_user, to_user=user.user, type=0)
        try:
            send_mail("项目审批提醒（管理员）", ele_user, email, [user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
    for user in admin:
        ele_user = "管理员-{examine_user}{add}了{tag}项目-{name}的审批申请。".format(
            examine_user=examine_user, tag=project.get_tag_display(), name=project.project_name, user=user_ele,
            add=add
        )
        models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
        try:
            send_mail("项目审批提醒（管理员）", ele_user, email, [user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)


@shared_task
def send_new_task(task):
    user_ele = ""
    create_user = task.created_user
    department = create_user.department
    to_users = models.TaskUser.objects.filter(task=task)
    for user in to_users:
        user_ele += "%s，" % user.user.first_name
    if task.project:
        project = task.project
        project_users = models.ProjectUser.objects.filter(project=project)
        admin = User.objects.filter(department=project.department, is_admin=True)
        ele_user = "{department}-{create_user}创建了{tag}项目-{name}所属任务：{task}，任务托付人为{user_ele}。".format(
            create_user=create_user, tag=project.get_tag_display(), name=project.project_name, user_ele=user_ele,
            department=department, task=task.name
        )
        for user in admin:
            models.Notice.objects.create(notice=ele_user, to_user=user, type=1)
            try:
                send_mail("新建任务提醒", ele_user, email, [user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)
        for user in project_users:
            models.Notice.objects.create(notice=ele_user, to_user=user.user, type=1)
            try:
                send_mail("新建任务提醒", ele_user, email, [user.user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
    else:
        ele_user = "{department}-{create_user}创建了任务：{task}，任务托付人为{user}。".format(department=department,
                                                                                 create_user=create_user, user=user_ele,
                                                                                 task=task.name
                                                                                 )
    for user in to_users:
        models.Notice.objects.create(notice=ele_user, to_user=user.user, type=1)
        try:
            send_mail("新建任务提醒", ele_user, email, [user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)


@shared_task
def send_task_status(task):
    user_ele = ""
    status = task.get_status_display()
    to_users = models.TaskUser.objects.filter(task=task)
    for user in to_users:
        user_ele += "%s，" % user.user.first_name
    if task.project:
        project = task.project
        project_users = models.ProjectUser.objects.filter(project=project)
        ele_user = "{tag}项目-{name}所属任务：{task}，任务状态变更为{status}。".format(task=task.name,
                                                                       tag=project.get_tag_display(),
                                                                       name=project.project_name, status=status)
        if task.status == 3:
            ele_user = "{tag}项目-{name}所属任务：{task}已结束，任务托付人为{user_ele}。".format(task=task.name,
                                                                               tag=project.get_tag_display(),
                                                                               name=project.project_name,
                                                                               user_ele=user_ele)
        elif task.status == 5:
            ele_user = "{tag}项目-{name}所属任务：{task}已暂停。".format(task=task.name, tag=project.get_tag_display(),
                                                              name=project.project_name)
        for user in project_users:
            models.Notice.objects.create(notice=ele_user, to_user=user.user, type=1)
            try:
                send_mail("任务状态变更提醒", ele_user, email, [user.user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
    else:
        ele_user = "任务：{task}，任务状态变更为{status}。".format(task=task.name, status=status)
        if task.status == 3:
            ele_user = "任务：{task}已结束，任务托付人为{user_ele}。".format(task=task.name, user_ele=user_ele)
    for user in to_users:
        models.Notice.objects.create(notice=ele_user, to_user=user.user, type=1)
        try:
            send_mail("任务状态变更提醒", ele_user, email, [user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)


@shared_task
def send_delay(delay):
    create_user = delay.created_user
    pass_user = delay.user
    task = delay.task
    department = create_user.department
    to_users = models.TaskUser.objects.filter(task=task)
    superuser = User.objects.filter(is_superuser=True)
    if delay.project:
        project = delay.project
        project_users = models.ProjectUser.objects.filter(project=project)
        admin = User.objects.filter(department=project.department, is_admin=True)
        if delay.type == "任务延期":
            add = "所属任务：{task}的延期申请".format(task=task.name)
        elif delay.type == "项目延期":
            add = "的延期申请"
        else:
            add = "所属节点：{node}的延期申请".format(node=delay.project_node)
        if delay.is_pass == None:
            for user in admin:
                ele = "{department}-{create_user}提交了{tag}项目-{name}{add},申请延时至{time}，" \
                      "需进行审批。".format(create_user=create_user, tag=project.get_tag_display(),
                                      name=project.project_name, department=department, task=task.name,
                                      time=delay.time, add=add)
                models.Notice.objects.create(notice=ele, to_user=user, type=1)
                try:
                    send_mail("任务延期申请提醒", ele, email, [user.email], fail_silently=False)
                except Exception:
                    models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)
            ele_user = "{department}-{create_user}提交了{tag}项目-{name}{add},申请延时至{time}".format(
                create_user=create_user, tag=project.get_tag_display(), name=project.project_name,
                department=department,
                task=task.name, time=delay.time, add=add)
        elif delay.is_pass == True:
            ele_user = "{department}-{pass_user}通过了{tag}项目-{name}{add},该任务将延期至{time}。".format(
                pass_user=pass_user, tag=project.get_tag_display(),
                name=project.project_name, department=pass_user.department, task=task.name,
                time=delay.time, add=add)
        else:
            ele_user = "{department}-{pass_user}拒绝了{tag}项目-{name}{add}。".format(
                pass_user=pass_user, tag=project.get_tag_display(),
                name=project.project_name, department=pass_user.department, task=task.name, add=add)
        for user in project_users:
            models.Notice.objects.create(notice=ele_user, to_user=user.user, type=1)
            try:
                send_mail("任务延期提醒", ele_user, email, [user.user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
    else:
        if delay.is_pass == None:
            for user in superuser:
                ele = "{create_user}提交了任务{task}的延期申请,申请延时至{time}，" \
                      "需进行审批。".format(create_user=create_user, task=task.name, time=delay.time)
                models.Notice.objects.create(notice=ele, to_user=user, type=1)
                try:
                    send_mail("任务延期申请提醒", ele, email, [user.email], fail_silently=False)
                except Exception:
                    models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)
            ele_user = "{department}-{create_user}提交了任务{task}的延期申请,申请延时至{time}".format(
                create_user=create_user, department=department,
                task=task.name, time=delay.time)
        elif delay.is_pass == True:
            ele_user = "{pass_user}通过了任务{task}的延期申请,该任务将延期至{time}。".format(
                pass_user=pass_user, task=task.name,
                time=delay.time)
        else:
            ele_user = "{pass_user}拒绝了任务{task}的延期申请。".format(
                pass_user=pass_user, department=department, task=task.name)
    for user in to_users:
        models.Notice.objects.create(notice=ele_user, to_user=user.user, type=1)
        try:
            send_mail("任务延期提醒", ele_user, email, [user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)


@shared_task
def send_project_status2(project):
    department = project.department
    to_users = models.ProjectUser.objects.filter(project=project)
    admin = User.objects.filter(department=department, is_admin=True)
    superuser = User.objects.filter(is_superuser=True)
    if project.status == 2:
        ele_user = "{tag}项目-{name}已延期！".format(
            tag=project.get_tag_display(), name=project.project_name)
        for user in to_users:
            models.Notice.objects.create(notice=ele_user, to_user=user.user, type=2)
            try:
                send_mail("项目延期提醒", ele_user, email, [user.user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
        for user in admin:
            models.Notice.objects.create(notice=ele_user, to_user=user, type=2)
            try:
                send_mail("项目延期提醒", ele_user, email, [user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)
        for user in superuser:
            models.Notice.objects.create(notice=ele_user, to_user=user, type=2)
            try:
                send_mail("项目延期提醒", ele_user, email, [user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)


@shared_task
def send_task_status2(task):
    to_users = models.TaskUser.objects.filter(task=task)
    if task.project:
        project = task.project
        department = project.department
        admin = User.objects.filter(department=department, is_admin=True)
        if task.status == 2:
            ele_user = "{tag}项目-{name}所属任务：{task}已延期！".format(
                tag=project.get_tag_display(), name=project.project_name, task=task)
            for user in to_users:
                models.Notice.objects.create(notice=ele_user, to_user=user.user, type=2)
                try:
                    send_mail("任务延期提醒", ele_user, email, [user.user.email], fail_silently=False)
                except Exception:
                    models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
            for user in admin:
                models.Notice.objects.create(notice=ele_user, to_user=user, type=2)
                try:
                    send_mail("任务延期提醒", ele_user, email, [user.email], fail_silently=False)
                except Exception:
                    models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)
    else:
        if task.status == 2:
            ele_user = "任务：{task}已延期！".format(task=task)
            for user in to_users:
                models.Notice.objects.create(notice=ele_user, to_user=user.user, type=2)
                try:
                    send_mail("任务延期提醒", ele_user, email, [user.user.email], fail_silently=False)
                except Exception:
                    models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)


@shared_task
def send_alert_task(task):
    user_ele = ""
    to_users = models.TaskUser.objects.filter(task=task)
    for user in to_users:
        user_ele += "%s，" % user.user.first_name
    if task.project:
        project = task.project
        project_users = models.ProjectUser.objects.filter(project=project)
        admin = User.objects.filter(department=project.department, is_admin=True)
        ele_user = "{tag}项目-{name}所属任务：{task}，即将到期！。".format(tag=project.get_tag_display(),
                                                             name=project.project_name, task=task.name)
        for user in admin:
            models.Notice.objects.create(notice=ele_user, to_user=user, type=1)
            try:
                send_mail("任务提醒", ele_user, email, [user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)
        for user in project_users:
            models.Notice.objects.create(notice=ele_user, to_user=user.user, type=1)
            try:
                send_mail("任务提醒", ele_user, email, [user.user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
    else:
        ele_user = "任务：{task}，即将到期！。".format(task=task.name)
    for user in to_users:
        models.Notice.objects.create(notice=ele_user, to_user=user.user, type=1)
        try:
            send_mail("任务提醒", ele_user, email, [user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)


@shared_task
def send_alert_project_node(project_node):
    project = project_node.project
    to_users = models.ProjectUser.objects.filter(project=project)
    admin = User.objects.filter(department=project.department, is_admin=True)
    superuser = User.objects.filter(is_superuser=True)
    ele_user = "{tag}项目-{name}的节点，{node},即将到期！。".format(tag=project.get_tag_display(),
                                                        name=project.project_name, node=project_node.name)
    for user in to_users:
        models.Notice.objects.create(notice=ele_user, to_user=user.user, type=0)
        try:
            send_mail("项目节点提醒", ele_user, email, [user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
    for user in admin:
        models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
        try:
            send_mail("项目节点提醒", ele_user, email, [user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)
    for user in superuser:
        models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
        try:
            send_mail("项目节点提醒", ele_user, email, [user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)


@shared_task
def send_project4(project):
    to_users = models.ProjectUser.objects.filter(project=project)
    admin = User.objects.filter(department=project.department, is_admin=True)
    superuser = User.objects.filter(is_superuser=True)
    ele_user = "{tag}项目-{name}被搁置。".format(tag=project.get_tag_display(),
                                           name=project.project_name)
    for user in to_users:
        models.Notice.objects.create(notice=ele_user, to_user=user.user, type=0)
        try:
            send_mail("项目搁置提醒", ele_user, email, [user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
    for user in admin:
        models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
        try:
            send_mail("项目搁置提醒", ele_user, email, [user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)
    for user in superuser:
        models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
        try:
            send_mail("项目搁置提醒", ele_user, email, [user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)


@shared_task
def send_project5(project):
    to_users = models.ProjectUser.objects.filter(project=project)
    admin = User.objects.filter(department=project.department, is_admin=True)
    superuser = User.objects.filter(is_superuser=True)
    ele_user = "{tag}项目-{name}已经被重启。".format(tag=project.get_tag_display(),
                                             name=project.project_name)
    for user in to_users:
        models.Notice.objects.create(notice=ele_user, to_user=user.user, type=0)
        try:
            send_mail("项目重启提醒", ele_user, email, [user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
    for user in admin:
        models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
        try:
            send_mail("项目重启提醒", ele_user, email, [user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)
    for user in superuser:
        models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
        try:
            send_mail("项目重启提醒", ele_user, email, [user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)


@shared_task
def send_task5(task):
    to_users = models.TaskUser.objects.filter(task=task)
    if task.project:
        project = task.project
        project_users = models.ProjectUser.objects.filter(project=project)
        ele_user = "{tag}项目-{name}所属任务：{task}，被重启！。".format(tag=project.get_tag_display(),
                                                            name=project.project_name, task=task.name)
        for user in project_users:
            models.Notice.objects.create(notice=ele_user, to_user=user.user, type=1)
            try:
                send_mail("任务重启提醒", ele_user, email, [user.user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
    else:
        ele_user = "任务：{task}，被重启！。".format(task=task.name)
    for user in to_users:
        models.Notice.objects.create(notice=ele_user, to_user=user.user, type=1)
        try:
            send_mail("任务重启提醒", ele_user, email, [user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)


@shared_task
def send_task4(task):
    to_users = models.TaskUser.objects.filter(task=task)
    if task.project:
        project = task.project
        project_users = models.ProjectUser.objects.filter(project=project)
        admin = User.objects.filter(department=project.department, is_admin=True)
        ele_user = "{tag}项目-{name}所属任务：{task}，被搁置！。".format(tag=project.get_tag_display(),
                                                            name=project.project_name, task=task.name)
        for user in admin:
            models.Notice.objects.create(notice=ele_user, to_user=user, type=1)
            try:
                send_mail("任务搁置提醒", ele_user, email, [user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)
        for user in project_users:
            models.Notice.objects.create(notice=ele_user, to_user=user.user, type=1)
            try:
                send_mail("任务搁置提醒", ele_user, email, [user.user.email], fail_silently=False)
            except Exception:
                models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)
    else:
        ele_user = "任务：{task}，被搁置！。".format(task=task.name)
    for user in to_users:
        models.Notice.objects.create(notice=ele_user, to_user=user.user, type=1)
        try:
            send_mail("任务搁置提醒", ele_user, email, [user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user.user, type=3)


@shared_task
def send_project6(project):
    admin = User.objects.filter(department=project.department, is_admin=True)
    superuser = User.objects.filter(is_superuser=True)
    ele_user = "{tag}项目-{name}距离开始时间还有一天，请尽快完成审核。".format(tag=project.get_tag_display(),
                                                          name=project.project_name)
    for user in admin:
        models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
        try:
            send_mail("项目重启提醒", ele_user, email, [user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)
    for user in superuser:
        models.Notice.objects.create(notice=ele_user, to_user=user, type=0)
        try:
            send_mail("项目重启提醒", ele_user, email, [user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=user, type=3)


@shared_task
def send_task_discuss(discuss):
    task = discuss.task
    to_users = models.TaskUser.objects.filter(task=task)
    if task.project:
        project = task.project
        ele_user = "{department}-{created}在{tag}项目-{name}所属任务：{task}中留言".format(created=discuss.created_user,
                                                                                tag=project.get_tag_display(),
                                                                                name=project.project_name, task=task,
                                                                                department=discuss.created_user.department)
    else:
        ele_user = "{department}-{created}在任务：{task}中留言".format(created=discuss.created_user, task=task,
                                                                department=discuss.created_user.department)
    for to_user in to_users:
        models.Notice.objects.create(notice=ele_user, to_user=to_user.user, type=1)


@shared_task
def send_project_discuss(discuss):
    project = discuss.project
    to_users = models.ProjectUser.objects.filter(project=project)
    ele_user = "{department}-{created}在{tag}项目-{name}中留言".format(created=discuss.created_user,
                                                                 tag=project.get_tag_display(),
                                                                 name=project.project_name,
                                                                 department=discuss.created_user.department)
    for to_user in to_users:
        models.Notice.objects.create(notice=ele_user, to_user=to_user.user, type=1)


@shared_task
def send_project_add_user(project_user):
    project = project_user.project
    to_users = models.ProjectUser.objects.filter(project=project)
    ele_user = "{department}-{user}加入到{tag}项目-{name}中".format(user=project_user.user, tag=project.get_tag_display(),
                                                              name=project.project_name,
                                                              department=project_user.user.department)
    for to_user in to_users:
        models.Notice.objects.create(notice=ele_user, to_user=to_user.user, type=0)
        try:
            send_mail("项目成员变更", ele_user, email, [to_user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=to_user.user, type=3)


@shared_task
def send_task_add_user(task_user):
    task = task_user.task
    to_users = models.TaskUser.objects.filter(task=task)
    if task.project:
        project = task.project
        ele_user = "{department}-{user}加入到{tag}项目-{name}所属任务：{task}中".format(user=task_user.user,
                                                                             tag=project.get_tag_display(),
                                                                             name=project.project_name, task=task,
                                                                             department=task_user.user.department)
    else:
        ele_user = "{department}-{user}加入到任务：{task}中".format(user=task_user.user, task=task,
                                                             department=task_user.user.department)
    for to_user in to_users:
        models.Notice.objects.create(notice=ele_user, to_user=to_user.user, type=0)
        try:
            send_mail("任务成员变更", ele_user, email, [to_user.user.email], fail_silently=False)
        except Exception:
            models.Notice.objects.create(notice="你的邮箱无法使用请及时更换", to_user=to_user.user, type=3)


@shared_task
def send_task_delay():
    projects = models.Project.objects.all()
    tasks = models.Task.objects.all()
    new = datetime.datetime.now()
    for project in projects:
        end_time = project.end_time
        start_time = project.start_time
        if project.status == 1:
            if end_time < new:
                project.status = 2
                project.save()
                project_logs.status_project(project)
                send_project_status2(project)
            project_nodes = models.ProjectNode.objects.filter(project=project)
            for project_node in project_nodes:
                alert_time = project_node.node_alert_time
                if alert_time:
                    if project_node.spare != '1':
                        if alert_time < new:
                            project_node.spare = 1
                            project_node.save()
                            send_alert_project_node(project_node)
        if project.status == 0:
            if project.spare != '1':
                if start_time < new - datetime.timedelta(days=1):
                    project.spare = 1
                    project.save()
                    send_project6(project)
            if start_time < new:
                project.status = 4
                project.save()
                project_logs.status_project(project)
                send_project4(project)
    for task in tasks:
        time = task.end_time
        alert_time = task.alert_time
        if task.status == 1:
            if time < new:
                task.status = 2
                task.save()
                task_logs.g_task(task)
                send_task_status2(task)
            if alert_time:
                if task.spare != '1':
                    if alert_time < new:
                        task.spare = 1
                        task.save()
                        send_alert_task(task)
        if task.status == 0:
            if time < new:
                task.status = 4
                task.save()
                task_logs.g_task(task)
                send_task4(task)
