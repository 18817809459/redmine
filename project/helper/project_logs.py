from project import models
from user.models import User


def new_project(project):
    project_log = models.ProjectLog(project=project)
    project_log.description = "创建了项目"
    project_log.created_user = project.created_user
    project_log.save()


def edit_project(changed_date, project, user):
    if changed_date:
        project_log = models.ProjectLog(project=project)
        project_log.description = "编辑了项目"
        project_log.created_user = user
        project_log.save()


def status_project(project):
    project_log = models.ProjectLog(project=project)
    if project.status == 4:
        project_log.description = "项目被搁置"
    elif project.status == 2:
        project_log.description = "项目已延期"
    project_log.save()

def statu_project(project,user):
    project_log = models.ProjectLog(project=project)
    if project.status == 3:
        project_log.description = "结束了项目"
        project_log.created_user = user
    project_log.save()

def supend_project(project,user):
    project_log = models.ProjectLog(project=project)
    project_log.description = "暂停了项目"
    project_log.created_user = user
    project_log.save()


def restart_project(project, user):
    project_log = models.ProjectLog(project=project)
    project_log.description = "重启了项目"
    project_log.created_user = user
    project_log.save()


def add_user(users, user, project):
    us = ''
    for user_id in users:
        user = User.objects.get(id=user_id)
        us += "%s，" % user.first_name
    project_log = models.ProjectLog(project=project)
    project_log.description = "添加项目托付人%s" % us
    project_log.created_user = user
    project_log.save()


def add_file(file, user, project):
    project_log = models.ProjectLog(project=project)
    project_log.description = "上传文件%s" % file.name
    project_log.file = file
    project_log.created_user = user
    project_log.save()


def add_node(project_node, user):
    project_log = models.ProjectLog(project=project_node.project)
    project_log.description = "添加项目节点：%s" % project_node.name
    project_log.created_user = user
    project_log.save()


def delay_project(delay):
    project_log = models.ProjectLog(project=delay.project)
    project_log.description = "创建了延期申请。申请延期至%s" % delay.time
    project_log.created_user = delay.created_user
    project_log.save()


def node_delay_project(delay):
    project_log = models.ProjectLog(project=delay.project)
    project_log.description = "创建了项目节点%s的延期申请。申请延期至%s" % (delay.project_node.name,delay.time)
    project_log.created_user = delay.created_user
    project_log.save()

def delay_pass(delay):
    project_log = models.ProjectLog(project=delay.project)
    if delay.is_pass:
        project_log.description = "通过了%s的延期申请，项目延期至%s" % (delay.created_user, delay.time)
    else:
        project_log.description = "拒绝了%s的延期申请" % delay.created_user
    project_log.created_user = delay.user
    project_log.save()


def node_delay_pass(delay):
    project_log = models.ProjectLog(project=delay.project)
    if delay.is_pass:
        project_log.description = "通过了项目节点%s的延期申请，项目延期至%s" % (delay.project_node.name, delay.time)
    else:
        project_log.description = "拒绝了项目节点%s的延期申请" % delay.project_node
    project_log.created_user = delay.user
    project_log.save()


def node_project(project, user):
    project_log = models.ProjectLog(project=project)
    no = '%s' % project.node
    if project.node_node:
        no += "-->%s" % project.node_node
    project_log.description = "变更项目节点为%s" % no
    project_log.created_user = user
    project_log.save()


def examine_project(examine):
    project_log = models.ProjectLog(project=examine.project)
    if examine.is_pass:
        pas = '通过了'
    else:
        pas = '被拒绝'
    if examine.examine == 0:
        project_log.description = "部门经理审批%s" % pas
    elif examine.examine == 1:
        project_log.description = "管理员审批%s" % pas
    project_log.created_user = examine.examine_user
    project_log.save()