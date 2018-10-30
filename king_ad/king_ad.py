#!/usr/bin/env python
# _*_conding:utf-8 _*_

from project import models as project
from user.models import User,Department,Role
enabled_admins = {}

class BaseAd(object):
    list_display = ['id',]
    list_filters = []
    search_fields = []
    list_per_page = 10
    label_display = []
    ordering = None
    filter_horizontal = ()
    readonly_table = False

class UserAd(BaseAd):
    list_display = ['first_name','department','duty','email','entry_time','is_active']
    list_filters = ['department', 'is_active']
    search_fields = ['first_name']
    label_display = ['姓名','所属部门','职务','邮箱地址','入职时间','账号状态']

class ProjectTypeAd(BaseAd):
    list_display = ['name','description','department']
    list_filters = ['department']
    search_fields = ['name']
    label_display = ['名称','描述','所属部门']

class TaskTypeAd(BaseAd):
    list_display = ['name', 'description', 'department']
    list_filters = ['department']
    search_fields = ['name']
    label_display = ['名称', '描述', '所属部门']

class ProjectFlowAd(BaseAd):
    list_display = ['flow_name','flow_description','department']
    list_filters = ['department']
    search_fields = ['flow_name']
    label_display = ['名称','描述','部门']

class ProjectAd(BaseAd):
    list_display = ['project_name','tag','project_type','examined','status','project_user','end_time','delay_status']
    list_filters = ['tag','status']
    search_fields = ['project_name']
    label_display = ['项目名称','项目所属','项目类型','审批流程','项目状态','项目托付','结束时间','延期申请']

class TaskAd(BaseAd):
    list_display = ['name','project','task_type','status','task_user','end_time','delay_status']
    list_filters = ['status']
    search_fields = ['name']
    label_display = ['任务名称','所属项目','任务类型','任务状态','任务托付','交付时间','延期申请']

class DepartmentAd(BaseAd):
    list_display = ['department_name']
    search_fields = ['department_name']
    label_display = ['名称']

class RoleAd(BaseAd):
    list_display = ['name']
    search_fields = ['name']
    label_display = ['名称']

class ExamineAd(BaseAd):
    list_display = ['project','created_user','examine','is_pass','created_time']
    list_filters = ['is_pass']
    label_display = ['项目名称','提交人','审批阶段','状态','创建时间']

class DelayAd(BaseAd):
    list_display = ['project_task','type','reason','time','is_pass']
    list_filters = ['type','is_pass']
    label_display = ['项目/任务名称','延期类型','延期理由','延期时间','状态']

class ContributionTypeAd(BaseAd):
    list_display = ['name','description','department']
    search_fields = ['name']
    label_display = ['名称','描述','所属部门']

class ContributionAd(BaseAd):
    list_display = ['name','type','created_user','created_time']
    search_fields = ['name']
    label_display = ['名称','类型','创建人','创建时间']

class FileAd(BaseAd):
    list_display = ['name','created_time']
    list_filters = ['postfix']
    search_fields = ['name']
    label_display = ['名称','创建时间']

def register(models_class,admin_class=None):

    if models_class._meta.app_label not in enabled_admins:
        enabled_admins[models_class._meta.app_label] = {}

    admin_class.model = models_class
    enabled_admins[models_class._meta.app_label][models_class._meta.model_name] = admin_class


register(User,UserAd)
register(Role,RoleAd)
register(project.ProjectType,ProjectTypeAd)
register(project.TaskType,TaskTypeAd)
register(project.ProjectFlow,ProjectFlowAd)
register(project.Project,ProjectAd)
register(project.Task,TaskAd)
register(Department,DepartmentAd)
register(project.Examine,ExamineAd)
register(project.Delay,DelayAd)
register(project.ContributionType,ContributionTypeAd)
register(project.Contribution,ContributionAd)
register(project.File,FileAd)