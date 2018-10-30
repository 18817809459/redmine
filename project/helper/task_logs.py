from project import models
from user.models import User


def new_task(task):
    task_log = models.TaskLog(task=task)
    task_log.description = "创建了任务"
    task_log.created_user = task.created_user
    task_log.save()

def edit_task(changed_date,task,user):
    if changed_date:
        task_log = models.TaskLog(task=task)
        task_log.description = "编辑了任务"
        task_log.created_user = user
        task_log.save()

def g_task(task):
    task_log = models.TaskLog(task=task)
    if task.status == 4:
        task_log.description = "超过结束时间未执行，任务被搁置"
    else:
        task_log.description = "更改任务状态为%s" % task.get_status_display()
    task_log.save()

def supend_project(task,user):
    task_log = models.TaskLog(task=task)
    task_log.description = "暂停了项目"
    task_log.created_user = user
    task_log.save()

def status_task(task,user):
    task_log = models.TaskLog(task=task)
    if task.status == 4:
        task_log.description = "超过结束时间未执行，任务被搁置"
    elif task.status == 3:
        task_log.description = "结束了任务"
        task_log.created_user = user
    else:
        task_log.description = "更改任务状态为%s" % task.get_status_display()
        task_log.created_user = user
    task_log.save()


def restart_task(task,user):
    task_log = models.TaskLog(task=task)
    task_log.description = "重启了任务，结束时间变更为%s" % task.end_time
    task_log.created_user = user
    task_log.save()

def add_user(users,user,task):
    us = ''
    for user_id in users:
        use = User.objects.get(id=user_id)
        us += "%s，" % use.first_name
    task_log = models.TaskLog(task=task)
    task_log.description = "添加项目托付人%s" % us
    task_log.created_user = user
    task_log.save()

def add_file(file,user,task):
    task_log = models.TaskLog(task=task)
    task_log.description = "上传文件%s" % file.name
    task_log.file = file
    task_log.created_user = user
    task_log.save()

def delay_task(delay):
    task_log = models.TaskLog(task=delay.task)
    task_log.description = "创建了延期申请。申请延期至%s" % delay.time
    task_log.created_user = delay.created_user
    task_log.save()

def delay_pass(delay):
    task_log = models.TaskLog(task=delay.task)
    if delay.is_pass:
        task_log.description = "通过了%s的延期申请，任务延期至%s" % (delay.created_user,delay.time)
    else:
        task_log.description = "拒绝了%s的延期申请" % delay.created_user
    task_log.created_user = delay.user
    task_log.save()