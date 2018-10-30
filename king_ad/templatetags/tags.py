#!/usr/bin/env python
# _*_conding:utf-8 _*_


from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import datetime, timedelta
from project import models as project
from django.contrib.auth import models
from user.models import Department, User
from django.urls import reverse
import datetime
from project.helper.helper import time_

register = template.Library()


# 权限判断
def hs_perms(request, perm):
    user = request.user
    if user.is_superuser:
        return True
    else:
        perm_list = []
        permissions = user.role.permission.all()
        for permission in permissions:
            perm_list += (permission.content_type.app_label + '.' + permission.codename,)
        if perm in perm_list:
            return True


# 用户身份判断
def can_delay(request, type, obj):
    if type == 'project':
        if request.path == '/':
            return False
        else:
            host_user = project.ProjectUser.objects.get(project=obj, is_host=True)
            if request.user.is_superuser:
                return True
            elif request.user.is_admin:
                if request.user.department == obj.department:
                    return True
                else:
                    return False
            else:
                if request.user == host_user.user:
                    return True
                else:
                    return False
    if type == 'task':
        host_user = project.TaskUser.objects.get(task=obj, is_host=True)
        if request.user.is_superuser:
            return True
        elif request.user.is_admin:
            if obj.project:
                if request.user.department == obj.project.department:
                    return True
                else:
                    return False
            else:
                return False
        else:
            if obj.project:
                project_host = project.ProjectUser.objects.get(project=obj.project, is_host=True)
                if request.user == project_host.user or request.user == host_user.user:
                    return True
                else:
                    return False
            else:
                if request.user == host_user.user:
                    return True
                else:
                    return False


# 获取所有数据
@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()


# 表格内容
@register.simple_tag
def build_table_row(request, obj, admin_class):
    table_name = admin_class.model._meta.verbose_name
    row_ele = ""
    for column in admin_class.list_display:
        if column == 'project_task':
            if table_name == "延期申请":
                typ = getattr(obj, 'type')
                if typ == "任务延期":
                    column_data = getattr(obj, 'task')
                else:
                    column_data = getattr(obj, 'project')
            elif table_name == "文件管理":
                if obj.task:
                    column_data = getattr(obj, 'task')
                else:
                    column_data = getattr(obj, 'project')
        elif column == 'first_name':
            user_id = getattr(obj, 'id')
            use = User.objects.get(id=user_id)
            column_data = "<img src='/media/{head}' alt='user' width='40' class='img-circle'/>&nbsp;&nbsp;{user}".format(
                head=use.head, user=use.first_name)
        elif column == 'task_user':
            task_id = getattr(obj, 'id')
            user_list = project.TaskUser.objects.filter(task=task_id)
            column_data = ""
            for user in user_list:
                column_data += "%s," % user.user
        elif column == 'project_user':
            project_id = getattr(obj, 'id')
            user_list = project.ProjectUser.objects.filter(project=project_id)
            column_data = ""
            for user in user_list:
                column_data += "%s," % user.user
        else:
            field_obj = obj._meta.get_field(column)
            if field_obj.choices:  # choices type
                if column == 'status':
                    if obj.status == 0:
                        column_data = "<span class='label label-warning' >%s</span>" % getattr(obj,
                                                                                               "get_%s_display" % column)()
                    elif obj.status == 1:
                        column_data = "<span class='label label-success' >%s</span>" % getattr(obj,
                                                                                               "get_%s_display" % column)()
                    elif obj.status == 2:
                        column_data = "<span class='label label-danger' style='background-color:#7465eb'>%s</span>" % getattr(
                            obj,
                            "get_%s_display" % column)()
                    elif obj.status == 3:
                        column_data = "<span class='label label-info' >%s</span>" % getattr(obj,
                                                                                            "get_%s_display" % column)()
                    elif obj.status == 4:
                        column_data = "<span class='label label-danger' >%s</span>" % getattr(obj,
                                                                                              "get_%s_display" % column)()
                    elif obj.status == 5:
                        column_data = "<span class='label label-inverse' >%s</span>" % getattr(obj,
                                                                                               "get_%s_display" % column)()
                    else:
                        column_data = getattr(obj, "get_%s_display" % column)()
                else:
                    column_data = getattr(obj, "get_%s_display" % column)()
            else:
                column_data = getattr(obj, column)
                if len(str(column_data)) > 60:
                    column_data = column_data[0:60]
            if type(column_data).__name__ == 'datetime':
                column_data = column_data.strftime("%Y/%m/%d %H:%M")
            if table_name == "用户":
                if type(column_data).__name__ == 'bool':
                    if column_data:
                        column_data = "正常"
                    else:
                        column_data = "禁用"
            if table_name == "项目审核" or table_name == "延期申请":
                if column == 'is_pass':
                    if column_data == None:
                        column_data = "<span class='label label-warning'>待审批</span>"
                    if type(column_data).__name__ == 'bool':
                        if column_data:
                            column_data = "<span class='label label-success'>已通过</span>"
                        else:
                            column_data = "<span class='label label-danger'>已拒绝</span>"
            if column_data == None:
                column_data = ""
        row_ele += "<td>%s</td>" % column_data
        if table_name == '项目':
            adds = ""
            if obj.status == 3 or obj.status == 0 or obj.status == 4 or obj.status == 5:
                adds = ""
            else:
                if request.user.is_superuser:
                    adds = "<a href='{request_path}{obj_id}/change/'><span class='label label-danger' " \
                           "style='background-color:#36d9d1;'>编辑</span></a>&nbsp;".format(
                        request_path=request.path, obj_id=obj.id)
                if request.user.is_admin:
                    if request.user.department == getattr(obj, 'department'):
                        adds = "<a href='{request_path}{obj_id}/change/'><span class='label label-danger'" \
                               " style='background-color:#36d9d1;'>编辑</span></a>&nbsp;".format(
                            request_path=request.path, obj_id=obj.id)
                if can_delay(request, 'project', obj):
                    adds += "<a data-target='#exampleModal' data-toggle='modal' data-remote='true' href='#'" \
                            " id='{obj_id}' onclick='delay(this)'><span class='label label-info'>延期申请</span></a>".format(
                        obj_id=obj.id)
            column = "<td><a href='{request_path}{obj_id}'><span class='label label-warning' >查看</span></a>&nbsp;" \
                     "{adds}</td>".format(
                request_path=request.path, adds=adds,
                obj_id=obj.id)
        elif table_name == '任务':
            adds = ""
            if obj.status == 3 or obj.status == 0 or obj.status == 4 or obj.status == 5:
                adds = ""
            else:
                if request.user.is_superuser:
                    adds = "<a href='{request_path}{obj_id}/change/'><span class='label label-danger' " \
                           "style='background-color:#36d9d1;'>编辑</span></a>&nbsp;".format(
                        request_path=request.path, obj_id=obj.id)
                if obj.project:
                    if request.user.department == obj.project.department and request.user.is_admin:
                        adds = "<a href='{request_path}{obj_id}/change/'><span class='label label-danger' " \
                               "style='background-color:#36d9d1;'>编辑</span></a>&nbsp;".format(
                            request_path=request.path, obj_id=obj.id)
                else:
                    if request.user == obj.created_user:
                        adds = "<a href='{request_path}{obj_id}/change/'><span class='label label-danger' " \
                               "style='background-color:#36d9d1;'>编辑</span></a>&nbsp;".format(
                            request_path=request.path, obj_id=obj.id)
                if can_delay(request, 'task', obj):
                    adds += "<a data-target='#exampleModal' data-toggle='modal' data-remote='true' href='#' id='{obj_id}'" \
                            " onclick='delay(this)'><span class='label label-info'>延期申请</span></a>".format(
                        obj_id=obj.id)
            column = "<td><a href='{request_path}{obj_id}'><span class='label label-warning' >查看</span></a>&nbsp;" \
                     "{adds}</td>".format(
                request_path=request.path, adds=adds,
                obj_id=obj.id)
        elif table_name == '项目审核' or table_name == '延期申请':
            if obj.is_pass == None:
                column = "<td><a href='{request_path}{obj_id}/change/'><span class='label label-primary' >审批</span></a></td>".format(
                    request_path=request.path,
                    obj_id=obj.id)
            else:
                column = "<td><a href='{request_path}{obj_id}/change/'><span class='label label-info' >查看</span></a></td>".format(
                    request_path=request.path,
                    obj_id=obj.id)
        elif table_name == '用户':
            column_user = "<a href='{request_path}{obj_id}/change/'><span class='label label-danger' " \
                          "style='background-color:#36d9d1;'>编辑</span></a>&nbsp;".format(
                request_path=request.path, obj_id=obj.id)
            if request.user.id != obj.id:
                if request.user.is_superuser or request.user.is_admin:
                    if obj.is_active:
                        column_user += "<a href='javascript:void(0)' onclick='active(this,{obj_id},0)'>" \
                                       "<span class='label label-warning' >禁用</span></a>".format(
                            request_path=request.path, obj_id=obj.id)
                    else:
                        column_user += "<a href='javascript:void(0)' onclick='active(this,{obj_id},1)'>" \
                                       "<span class='label label-info' >启用</span></a>".format(
                            request_path=request.path, obj_id=obj.id)
            column = "<td>%s</td>" % column_user
        elif table_name == '文件管理':
            column = "<td><a href='/media/{file}' download='{name}'><span class='label label-danger'  " \
                     "style='background-color:#36d9d1;'>下载</span></a></td>".format(
                file=obj.file, name=obj.name)
        elif table_name == '贡献':
            column = "<td><a href='{request_path}{obj_id}'><span class='label label-warning' >查看</span></a>&nbsp;" \
                     "<a href='{request_path}{obj_id}/change/'><span class='label label-danger'" \
                     " style='background-color:#36d9d1;' >编辑</span></a></td>".format(
                request_path=request.path,
                obj_id=obj.id)
        else:
            column = "<td><a href='{request_path}{obj_id}/change/'><span class='label label-danger'" \
                     " style='background-color:#36d9d1;' >编辑</span></a></td>".format(
                request_path=request.path, obj_id=obj.id)
    row_ele += column
    return mark_safe(row_ele)


# 组合查询
@register.simple_tag
def render_filter_ele(condtion, admin_class, filter_condtions, request):
    table_name = admin_class.model._meta.verbose_name
    req = str(request)
    num = req.find('sta')
    if num > 0:
        sta = req[num + 4:num + 5]
    else:
        sta = ''
    if condtion == 'status' and sta == '0':
        select_ele = ''
    elif table_name == '项目流程' and condtion == 'department' and request.user.is_superuser == False:
        select_ele = ''
    elif table_name == '任务类型' and condtion == 'department' and request.user.is_superuser == False:
        select_ele = ''
    elif table_name == '项目类型' and condtion == 'department' and request.user.is_superuser == False:
        select_ele = ''
    elif table_name == '用户' and condtion == 'department' and request.user.is_superuser == False:
        select_ele = ''
    else:
        if condtion == 'project':
            select_ele = '''<select class="form-control m-t-10" name='{filter_field}' ><option value='' style="display:none;">所属项目</option>'''
        elif condtion == 'status':
            select_ele = '''<select class="form-control m-t-10" name='{filter_field}' ><option value='' style="display:none;">状态</option>'''
        elif condtion == 'department' or condtion == 'department_id':
            select_ele = '''<select class="form-control m-t-10" name='{filter_field}' ><option value='' style="display:none;">所属部门</option>'''
        elif condtion == 'tag':
            select_ele = '''<select class="form-control m-t-10" name='{filter_field}' ><option value='' style="display:none;">项目所属</option>'''
        elif condtion == 'is_active':
            select_ele = '''<select class="form-control m-t-10" name='{filter_field}' ><option value='' style="display:none;">账号状态</option>'''
        elif condtion == 'is_pass':
            select_ele = '''<select class="form-control m-t-10" name='{filter_field}' ><option value='' style="display:none;">状态</option>'''
        elif condtion == 'type':
            select_ele = '''<select class="form-control m-t-10" name='{filter_field}' ><option value='' style="display:none;">延期类型</option>'''
        elif condtion == 'postfix':
            select_ele = '''<select class="form-control m-t-10" name='{filter_field}' ><option value='' style="display:none;">文件类型</option>'''
        elif condtion == 'created_time':
            select_ele = '''<select class="form-control m-t-10" name='{filter_field}' ><option value='' style="display:none;">创建时间</option>'''
        else:
            select_ele = '''<select class="form-control m-t-10" name='{filter_field}' ><option value='' style="display:none;">------</option>'''
        field_obj = admin_class.model._meta.get_field(condtion)
        if condtion == 'type':
            if filter_condtions.get(condtion) == '任务延期':
                select1 = "<option value='任务延期' selected>任务延期</option>"
                select2 = "<option value='项目延期'>项目延期</option>"
                select3 = "<option value='节点延期'>节点延期</option>"
            elif filter_condtions.get(condtion) == '项目延期':
                select1 = "<option value='任务延期'>任务延期</option>"
                select2 = "<option value='项目延期' selected>项目延期</option>"
                select3 = "<option value='节点延期'>节点延期</option>"
            elif filter_condtions.get(condtion) == '节点延期':
                select1 = "<option value='任务延期'>任务延期</option>"
                select2 = "<option value='项目延期'>项目延期</option>"
                select3 = "<option value='节点延期' selected>节点延期</option>"
            else:
                select3 = "<option value='节点延期'>节点延期</option>"
                select1 = "<option value='任务延期'>任务延期</option>"
                select2 = "<option value='项目延期'>项目延期</option>"
            select_ele += select3 + select1 + select2
        if condtion == 'postfix':
            files = project.File.objects.filter(existent=1)
            postfixs = []
            for file in files:
                postfixs.append(file.postfix)
            postfixs = list(set(postfixs))
            for postfix in postfixs:
                if filter_condtions.get(condtion) == postfix:
                    selected = "selected"
                else:
                    selected = ''
                select_ele += '''<option value='%s' %s>%s</option>''' % (postfix, selected, postfix)
        if field_obj.choices:
            for choice_item in field_obj.choices:
                li = []
                if condtion == 'status':
                    if sta == '1':
                        li = [0, 3, 4]
                    elif sta == '3':
                        li = [0, 1, 2, 5]
                if choice_item[0] not in li:
                    if filter_condtions.get(condtion) == str(choice_item[0]):
                        selected = "selected"
                    else:
                        selected = ''
                    select_ele += '''<option value='%s' %s>%s</option>''' % (choice_item[0], selected, choice_item[1])
        if type(field_obj).__name__ == "NullBooleanField":
            if filter_condtions.get(condtion) == '1':
                select1 = "<option value='1' selected>已通过</option>"
                select2 = "<option value='0'>已拒绝</option>"
                select3 = "<option value='None'>待审核</option>"
            elif filter_condtions.get(condtion) == '0':
                select1 = "<option value='1'>已通过</option>"
                select2 = "<option value='0' selected>已拒绝</option>"
                select3 = "<option value='None'>待审核</option>"
            elif filter_condtions.get(condtion) == 'None':
                select1 = "<option value='1'>已通过</option>"
                select2 = "<option value='0'>未通过</option>"
                select3 = "<option value='None' selected>待审核</option>"
            else:
                select3 = "<option value='None' >待审核</option>"
                select1 = "<option value='1'>已通过</option>"
                select2 = "<option value='0'>已拒绝</option>"
            select_ele += select3 + select1 + select2
        if type(field_obj).__name__ == "BooleanField":
            if filter_condtions.get(condtion) == '1':
                select1 = "<option value='1' selected>正常</option>"
                select2 = "<option value='0'>禁用</option>"
            elif filter_condtions.get(condtion) == '0':
                select1 = "<option value='1'>正常</option>"
                select2 = "<option value='0' selected>禁用</option>"
            else:
                select1 = "<option value='1'>正常</option>"
                select2 = "<option value='0'>禁用</option>"
            select_ele += select1 + select2
        if type(field_obj).__name__ == "ForeignKey":
            selected = ''
            for choice_item in field_obj.get_choices()[1:]:
                if filter_condtions.get(condtion) == str(choice_item[0]):
                    selected = "selected"
                select_ele += '''<option value='%s' %s>%s</option>''' % (choice_item[0], selected, choice_item[1])
                selected = ''
        if type(field_obj).__name__ in ['DateTimeField', 'DateField']:
            date_els = []
            today_ele = datetime.datetime.now().date()
            date_els.append(['今天', datetime.datetime.now().date()])
            # date_els.append(['昨天', today_ele - timedelta(days=1)])
            date_els.append(['7天内', today_ele - timedelta(days=7)])
            date_els.append(['15天内', today_ele - timedelta(days=15)])
            date_els.append(['一个月内', today_ele - timedelta(days=30)])
            date_els.append(['三个月内', today_ele - timedelta(days=30)])
            date_els.append(['半年内', today_ele - timedelta(days=180)])
            date_els.append(['一年内', today_ele - timedelta(days=365)])
            # date_els.append(['mtd_ele', today_ele.replace(day=1)])
            # date_els.append(['ytd_ele', today_ele.replace(month=1, day=1)])
            filter_field_name = "%s__gte" % condtion
            for item in date_els:
                if str(item[1]) == str(filter_condtions.get(filter_field_name)):
                    selected = 'selected'
                else:
                    selected = ''
                select_ele += '''<option value='%s' %s>%s</option>''' % (item[1], selected, item[0])
        else:
            filter_field_name = condtion
        select_ele += "</select>"
        select_ele = select_ele.format(filter_field=filter_field_name)
    return mark_safe(select_ele)


# 列表页数
@register.simple_tag
def build_paginators(query_sets, filter_condtions, precious_orderby, search_text, request):
    req = str(request)
    num = req.find('sta')
    if num > 0:
        sta = '&%s' % req[num:num + 5]
    else:
        sta = ''
    if request.GET.get('type'):
        sta = '&type=%s' % request.GET.get('type')
    pages_btns = ''
    filters = '%s' % sta
    addedd_dot_ele = False
    for k, v in filter_condtions.items():
        if k == 'created_time__range':
            a1 = v[0].strftime("%Y-%m-%d")
            a2 = v[1].strftime("%Y-%m-%d")
            v = str(a1) + ' ~ ' + str(a2)
        filters += "&%s=%s" % (k, v)
    if query_sets.has_previous():
        pages_btns += '''<a class="paginate_button previous" href="?page=%s%s&o=%s&_q=%s" style="width: 66px;">%s</a>''' % (
            query_sets.previous_page_number(), filters, precious_orderby, search_text, '上页')
    for page_num in query_sets.paginator.page_range:
        if page_num < 3 or page_num > query_sets.paginator.num_pages - 2 or abs(query_sets.number - page_num) <= 2:
            ele_class = ""
            if query_sets.number == page_num:
                addedd_dot_ele = False
                ele_class = "current"
            pages_btns += '''<a class="paginate_button %s" href="?page=%s%s&o=%s&_q=%s">%s</a>''' % (
                ele_class, page_num, filters, precious_orderby, search_text, page_num)
        else:
            if addedd_dot_ele == False:
                pages_btns += '<a class="paginate_button disabled">...</a>'
                addedd_dot_ele = True
    if query_sets.has_next():
        pages_btns += '''<a class="paginate_button next" href="?page=%s%s&o=%s&_q=%s" style="width: 66px;">%s</a>''' % (
            query_sets.next_page_number(), filters, precious_orderby, search_text, '下页')

    return mark_safe(pages_btns)


@register.simple_tag
def build_table_header_column(column, orderby_key, filter_condtions):
    filters = ''
    for k, v in filter_condtions.items():
        filters += "&%s=%s" % (k, v)
    if orderby_key:
        if orderby_key.startswith("-"):
            sort_icon = '''<span class="glyphicon glyphicon-chevron-up" aria-hidden="true"></span>'''
        else:
            sort_icon = '''<span class="glyphicon glyphicon-chevron-down" aria-hidden="true"></span>'''
        if orderby_key.strip("-") == column:
            orderby_key = orderby_key
        else:
            orderby_key = column
            sort_icon = ''
    else:
        orderby_key = column
        sort_icon = ''
    ele = '''<th>%s</th>''' % (column)
    return mark_safe(ele)


# 获取表名
@register.simple_tag
def get_model_name(admin_class):
    return admin_class.model._meta.verbose_name


@register.simple_tag
def get_m2m_obj_list(admin_class, field):
    field_obj = getattr(admin_class, field.name)
    return field_obj.rel.through.objects.all()


@register.simple_tag
def get_m2m_selected_obj_list(obj, field):
    try:
        field_obj = getattr(obj.instance, field.name)
    except ValueError:
        return None
    else:
        return field_obj.all()


@register.simple_tag
def display_obj_related(objs):
    '''把对象及所有相关联的数据取出来'''
    # objs = [objs,] #fake
    if objs:
        model_class = objs[0]._meta.model
        mode_name = objs[0]._meta.model_name
        return mark_safe(recursive_related_objs_lookup(objs))


# 角色权限列表
@register.simple_tag
def permissions_table(*args):
    no_show = ['项目', '任务', '贡献', '项目类型', '任务类型', '贡献类型', '项目流程', '项目审核', '延期申请']
    ele = ''
    content_types = models.ContentType.objects.filter(app_label='project')
    for content_type in content_types:
        if content_type.name in no_show:
            column = " <td>{obj}</td>".format(obj=content_type)
            content_type_id = content_type.id
            content_type_permissions = models.Permission.objects.filter(content_type_id=content_type_id).exclude(
                codename__contains="delete")
            for content_type_permission in content_type_permissions:
                if args:
                    if content_type_permission in args[0]:
                        column += "<td><input type='checkbox' id='permission_{obj_id}' name='permission' value='{obj_id}'checked><label for='permission_{obj_id}'></label></td>".format(
                            obj_id=content_type_permission.id)
                    else:
                        column += "<td><input type='checkbox' id='permission_{obj_id}' name='permission' value='{obj_id}'><label for='permission_{obj_id}'></label></td>".format(
                            obj_id=content_type_permission.id)
                else:
                    column += "<td><input type='checkbox' id='permission_{obj_id}' name='permission' value='{obj_id}'><label for='permission_{obj_id}'></label></td>".format(
                        obj_id=content_type_permission.id)
            ele += "<tr>" + column + "</tr>"
    return mark_safe(ele)


# 部门列表
@register.simple_tag
def department_list():
    departments = Department.objects.all()
    column = ""
    for department in departments:
        user_url = reverse('department_user', kwargs={'id': department.id})
        column += "<li><a href='{url}?department={id}'>{name} </a></li>".format(url=user_url, id=department.id,
                                                                                name=department)
    return mark_safe(column)


@register.simple_tag
def getattrs(obj, column):
    column_data = getattr(obj, column)
    return mark_safe(column_data)


# 员工多选框内列表
@register.simple_tag
def users(request, *args):
    ids = [0]
    if args:
        for project_user in args[0]:
            ids.append(project_user.user_id)
    departments_list = Department.objects.all()
    ele = ""
    user_department = request.user.department
    for user in User.objects.filter(department=None, is_active=True):
        if user.id not in ids:
            ele += "<option value='{id}'>{name}</option>".format(id=user.id, name=user)
    if user_department:
        column_user = ""
        for user in User.objects.filter(department=user_department, is_active=True):
            if user.id not in ids:
                column_user += "<option value='{id}'>{name}</option>".format(id=user.id, name=user)
        column = "<optgroup label='{name}'>{column}</optgroup>".format(name=user_department.department_name,
                                                                       column=column_user)
        ele += column
    for department in departments_list:
        if user_department != department:
            column_user = ""
            for user in User.objects.filter(department=department, is_active=True):
                if user.id not in ids:
                    column_user += "<option value='{id}'>{name}</option>".format(id=user.id, name=user)
            column = "<optgroup label='{name}'>{column}</optgroup>".format(name=department.department_name,
                                                                           column=column_user)
            ele += column
    return mark_safe(ele)


# 站内信
@register.simple_tag
def notice(user):
    notices = project.Notice.objects.filter(to_user=user, read=False).order_by('-created_time')[:3]
    ele = ""
    for noti in notices:
        if noti.type == 0:
            add = "<div class ='btn btn-success btn-circle' style='width:50px;height:50px;padding: 13px;margin-right: 16px;'>" \
                  "<i class='mdi mdi-gmail' style='font-size: 1.5rem;'></i></div>"
        elif noti.type == 1:
            add = "<div class ='btn btn-warning btn-circle' style='width:50px;height:50px;padding: 13px;margin-right: 16px;'>" \
                  "<i class='mdi mdi-file-document-box' style='font-size: 1.5rem;'></i></div>"
        elif noti.type == 2:
            add = "<div class ='btn btn-danger btn-circle' style='width:50px;height:50px;padding: 13px;margin-right: 16px;'>" \
                  "<i class='mdi mdi-timelapse' style='font-size: 1.5rem;'></i></div>"
        elif noti.type == 3:
            add = "<div class ='btn btn-info btn-circle' style='width:50px;height:50px;padding: 13px;margin-right: 16px;'>" \
                  "<i class='mdi mdi-send' style='font-size: 1.5rem;'></i></div>"
        ele += "<a href='{url}'>{add}" \
               "<div class='mail-contnet'><h5>{type}通知</h5> <span class='mail-desc'>{notice}</span>" \
               "<span class='time'>{time}</span></div></a>".format(type=noti.get_type_display(),
                                                                   notice=noti.notice, time=time_(noti.created_time),
                                                                   url=reverse('notice'),
                                                                   add=add)
    return mark_safe(ele)


# 站内信时间
@register.simple_tag
def notice_time(created_time):
    ele = time_(created_time)
    return mark_safe(ele)


# 导航栏
@register.simple_tag
def index(request):
    ele = ""
    if hs_perms(request, 'project.view_examine') or hs_perms(request, 'project.view_delay'):
        ele += "<li><a class='has-arrow waves-effect waves-dark' href='#' aria-expanded='false'>" \
               "<i class='mdi mdi-camera-iris'></i><span class='hide-menu'>审核</span></a>"
        ele_e = ""
        if hs_perms(request, 'project.view_examine'):
            ele_e += "<li><a href='%s'>项目审核 </a></li>" % reverse('examine')
        if hs_perms(request, 'project.view_delay'):
            ele_e += "<li><a href='%s'>延期审核 </a></li>" % reverse('delay')
        ele += "<ul aria-expanded='false' class='collapse'>%s </ul></li>" % ele_e
    if request.user.is_admin or request.user.is_superuser:
        ele += "<li><a class='has-arrow waves-effect waves-dark' href='%s'aria-expanded='false'>" \
               "<i class='mdi mdi-account-multiple'></i><span class='hide-menu'>员工</span></a></li>" % reverse(
            'auth_user')
    if hs_perms(request, 'project.view_projectflow'):
        ele += "<li><a class='has-arrow waves-effect waves-dark' href='%s'aria-expanded='false'>" \
               "<i class='mdi mdi-opacity'></i><span class='hide-menu'>项目流程</span></a></li>" % reverse('flow')
    if hs_perms(request, 'project.view_projecttype') or hs_perms(request, 'project.view_tasktype') or \
            hs_perms(request, 'project.view_contributiontype'):
        ele += "<li><a class='has-arrow waves-effect waves-dark' href='#' aria-expanded='false'>" \
               "<i class='mdi mdi-settings'></i><span class='hide-menu'>配置</span></a>"
        ele_e = ""
        if hs_perms(request, 'project.view_projecttype'):
            ele_e += "<li><a href='%s'>项目类型 </a></li>" % reverse('table_objs', kwargs={
                'app_name': 'project', 'table_name': 'projecttype'})
        if hs_perms(request, 'project.view_tasktype'):
            ele_e += "<li><a href='%s'>任务类型 </a></li>" % reverse('table_objs', kwargs={
                'app_name': 'project', 'table_name': 'tasktype'})
        if hs_perms(request, 'project.view_contributiontype'):
            ele_e += "<li><a href='%s'>贡献类型 </a></li>" % reverse('table_objs', kwargs={
                'app_name': 'project', 'table_name': 'contributiontype'})
        if request.user.is_superuser:
            ele_e += "<li><a href='%s'>角色 </a></li>" % reverse('role')
        ele += "<ul aria-expanded='false' class='collapse'>%s </ul></li>" % ele_e
    return mark_safe(ele)


# 任务留言文件
@register.simple_tag
def task_discuss(obj):
    ele = ''
    files = project.TaskDiscussFile.objects.filter(task_discuss=obj)
    for file in files:
        ele += '''<div class="row" style="padding-top:5px;font-size: 0.9rem">{name}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
           <a href="/media/{path}" download="{name}">下载</a></div>'''.format(
            name=file.file.name, path=file.file.file
        )
    return mark_safe(ele)


# 项目留言文件
@register.simple_tag
def project_discuss(obj):
    ele = ''
    files = project.ProjectDiscussFile.objects.filter(project_discuss=obj)
    for file in files:
        ele += '''<div class="row" style="padding-top:5px;font-size: 0.9rem">{name}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <a href="/media/{path}" download="{name}">下载</a></div>'''.format(
            name=file.file.name, path=file.file.file
        )
    return mark_safe(ele)


# 时间搜索
@register.simple_tag
def time_search(filter_condtions, precious_orderby, search_text, request):
    req = str(request)
    num = req.find('sta')
    if num > 0:
        sta = '&%s' % req[num:num + 5]
    else:
        sta = ''
    if request.GET.get('type'):
        sta = '&type=%s' % request.GET.get('type')
    pages_btns = ''
    filters = '%s' % sta
    for k, v in filter_condtions.items():
        if k != 'created_time__gte' and k != 'created_time__range':
            filters += "&%s=%s" % (k, v)
    date_els = []
    today_ele = datetime.datetime.now().date()
    date_els.append(['今天', datetime.datetime.now().date()])
    # date_els.append(['昨天', today_ele - timedelta(days=1)])
    date_els.append(['7天', today_ele - timedelta(days=7)])
    date_els.append(['15天', today_ele - timedelta(days=15)])
    date_els.append(['30天', today_ele - timedelta(days=30)])
    # date_els.append(['三个月内', today_ele - timedelta(days=30)])
    # date_els.append(['半年内', today_ele - timedelta(days=180)])
    # date_els.append(['一年内', today_ele - timedelta(days=365)])
    # date_els.append(['mtd_ele', today_ele.replace(day=1)])
    # date_els.append(['ytd_ele', today_ele.replace(month=1, day=1)])
    for item in date_els:
        if str(item[1]) == request.GET.get('created_time__gte'):
            selected = ''
        else:
            selected = 'color:#67757c'
        pages_btns += '''<div><a href="?created_time__gte=%s%s&o=%s&_q=%s"
        class="btn m-t-10" id="all" style="%s">%s</a></div>''' % (
            item[1], filters, precious_orderby, search_text, selected, item[0])
    pages_btns += '''<div class="form-group example"><div class="input-group"><div class="input-daterange input-group" id="date-range">
    <input type="text" class="form-control m-t-10" placeholder="时间范围" name="created_time__range" value="" 
    style="min-width:245px;"
    id="time_range"><span class="input-group-text" style="height:  40px;margin-top: 10px;"><i class="icon-calender">
    </i></span></div></div></div>'''
    return mark_safe(pages_btns)


@register.simple_tag
def show_btn(request, type, obj):
    ele = ''
    if can_delay(request, type, obj):
        if type == 'task':
            if obj.status == 0:
                ele += '''<button type="button" class="btn btn-success" onclick="zhix()" id="btn"> 执行任务</button>'''
            elif obj.status == 1 or obj.status == 2:
                ele += '''<button type="submit" class="btn btn-info" onclick="supen()">暂停任务</button>
                <button type="button" class="btn btn-primary" onclick="zhix()" id="btn"> 结束任务</button>'''
            elif obj.status == 4 or obj.status == 5:
                ele += '''<button type="button" class="btn btn-success" onclick="change()" id="btn">重启任务</button>
                <button type="button" class="btn btn-info" onclick="zhix()" id="btn2"> 关闭任务</button>'''
        elif type == 'project':
            if obj.status == 1 or obj.status == 2:
                ele += '''<button type="button" class="btn btn-success" onclick="change_node()">变更节点</button>
                <button type="submit" class="btn btn-info" onclick="supen()">暂停项目</button>
                <button type="submit" class="btn btn-primary">结束项目</button><a href="javascript:void(0)" 
                data-toggle="modal" data-target="#myModal" class="btn btn-warning text-white" style="margin-left: 5px;">
                上传</a>'''
            elif obj.status == 4 or obj.status == 5:
                ele += '''<button type="button" class="btn btn-success" onclick="chong()">重启项目</button>
                <button type="submit" class="btn btn-info">关闭项目</button>'''
    return mark_safe(ele)
