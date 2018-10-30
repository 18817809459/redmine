from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.backends import ModelBackend
from user.models import User, Department, Role, SessionUser,Csrf
from django.db.models import Q
from user.decorators import login_required
from user.forms import UserForm, UF, DepartmentForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
from king_ad.views import obj
from django.contrib.auth.models import Permission
import re
from project import tasks
from user import helper


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(email=username) | Q(username=username) | Q(phone=username))
        except User.DoesNotExist:  # 可以捕获除与程序退出sys.exit()相关之外的所有异常
            return None
        if user.is_active:
            if user.check_password(password):
                return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        res = auth.authenticate(username=username, password=password)
        if res is not None:
            auth.login(request, res)
            Csrf.objects.create(session=request.session.session_key, csrf='aa')
            return redirect('/', {'user': res})
        else:
            return render(request, 'login.html', {'login_error': '用户名或密码错误，请重新输入'})
    return render(request, 'login.html')


def reset(request):
    error = ''
    if request.method == 'POST':
        user = User.objects.filter(email=request.POST.get('email'))
        if user:
            password = request.POST.get('password')
            password_p = re.compile(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,10}")
            if password_p.match(password):
                user.set_password(request.POST['password'])
                user.save()
                return redirect(reverse('index'))
            else:
                error = "密码必须包含大小写字母和数字的组合，不能使用特殊字符，长度在8-10之间"
        else:
            error = "用户不存在"
    return render(request,'reset.html',{'error':error})



def logout(request):
    auth.logout(request)
    return redirect('/login/')


@login_required(login_url='/login/')
def user_obj(request):
    app_name = 'user'
    table_name = 'user'
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


@login_required(login_url='/login/')
def user_add(request):
    errors = ""
    user_form = UserForm()
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES)
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            password_p = re.compile(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,10}")
            password = request.POST.get('password')
            if password_p.match(password):
                if user_form.is_valid():
                    user_form.save()
                    user = User.objects.get(email=request.POST.get('email'))
                    role = Role.objects.get(id=1)
                    user.username = request.POST.get('last_name')
                    user.is_active = True
                    user.role = role
                    user.set_password(request.POST['password'])
                    user.save()
                    tasks.send_user.delay(user, request.POST['password'])
                    return redirect(request.path.replace('/add/', "/"))
                else:
                    errors = user_form.errors
            else:
                errors = "密码必须包含大小写字母和数字的组合，不能使用特殊字符，长度在8-10之间"
    return render(request, 'user_change.html', {'user_forms': user_form, 'errors': errors})


@login_required(login_url='/login/')
def user_edit(request, id):
    errors = ''
    user = User.objects.get(id=id)
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=user)
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if request.POST.get('password'):
                password_p = re.compile(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,10}")
                password = request.POST.get('password')
                if password_p.match(password):
                    if user_form.is_valid():
                        user_form.save()
                        user.set_password(request.POST['password'])
                        user.save()
                        return redirect(reverse('auth_user'))
                    else:
                        errors = user_form.errors
                else:
                    errors = "密码必须包含大小写字母和数字的组合，不能使用特殊字符，长度在8-10之间"
            else:
                if user_form.is_valid():
                    user_form.save()
                    return redirect(reverse('auth_user'))
                else:
                    errors = user_form.errors
    else:
        user_form = UserForm(instance=user)
    return render(request, 'user_change.html', {'user_forms': user_form, 'use': user, 'errors': errors})


@login_required(login_url='/login/')
def personal(request):
    errors = ''
    user = request.user
    if request.method == 'POST':
        user_form = UF(request.POST, request.FILES, instance=user)
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if user_form.is_valid():
                user_form.save()
                if request.POST.get('password'):
                    if user.check_password(request.POST.get('password')):
                        return user
                    else:
                        try:
                            user.set_password(request.POST['password'])
                            user.save()
                            return redirect(reverse('auth_user'))
                        except Exception:
                            errors = Exception
            else:
                errors = user_form.errors
    else:
        user_form = UF(instance=user)
    return render(request, 'personal.html', {'user_forms': user_form, 'use': user, 'errors': errors})


@login_required(login_url='/login/')
def depertment(request):
    request.GET._mutable = True
    request.GET["is_active"] = True
    ids = []
    departments = Department.objects.all()
    departments_id = 0
    app_name = 'user'
    table_name = 'user'
    count = helper.department()
    admin_class, query_sets, filter_condtions, orderby_key = obj(request, app_name, table_name, ids, departments_id)
    return render(request, 'project/department.html', {'admin_class': admin_class,
                                                       'query_sets': query_sets,
                                                       'filter_condtions': filter_condtions,
                                                       'orderby_key': orderby_key,
                                                       'precious_orderby': request.GET.get("o", ''),
                                                       'search_text': request.GET.get('_q', ''),
                                                       'departments': departments,
                                                       'count': count})


@login_required(login_url='/login/')
def role_obj(request):
    app_name = 'user'
    table_name = 'role'
    admin_class, query_sets, filter_condtions, orderby_key = obj(request, app_name, table_name)
    return render(request, 'project/project_objs.html', {'admin_class': admin_class,
                                                         'query_sets': query_sets,
                                                         'filter_condtions': filter_condtions,
                                                         'orderby_key': orderby_key,
                                                         'precious_orderby': request.GET.get("o", ''),
                                                         'search_text': request.GET.get('_q', ''),
                                                         'table_name': table_name})


# 新建角色
@login_required(login_url='/login/')
def role_add(request):
    if request.method == 'POST':
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            role = Role.objects.create(name=request.POST.get('name'))
            for permission_id in request.POST.getlist('permission'):
                permission = Permission.objects.get(id=permission_id)
                role.permission.add(permission)
            return redirect(reverse('role'))
    return render(request, 'role_permission.html')


# 编辑角色
@login_required(login_url='/login/')
def role_permission(request, id):
    errors = ''
    role = Role.objects.get(id=id)
    if request.method == 'POST':
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            role.name = request.POST.get('name')
            role.save()
            for permission in role.permission.all():
                role.permission.remove(permission)
            for permission_id in request.POST.getlist('permission'):
                permission = Permission.objects.get(id=permission_id)
                role.permission.add(permission)
    return render(request, 'role_permission.html', {'role': role, 'errors': errors})


# 新建部门
@login_required(login_url='/login/')
def department_add(request):
    if request.method == 'POST':
        department_form = DepartmentForm(request.POST)
        csrf = Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if department_form.is_valid():
                department_form.save()
                department = Department.objects.get(department_name=request.POST['department_name'])
                return redirect(reverse('department_user', kwargs={'id': department.id}) + '?department=%s' % department.id)
    else:
        department_form = DepartmentForm()
    return render(request, 'project/department_edit.html', {'department_form': department_form})


# 编辑部门
@login_required(login_url='/login/')
@csrf_exempt
def department_edit(request, id):
    if request.is_ajax():
        department = Department.objects.get(id=id)
        department.department_name = request.POST.get('name')
        department.save()
        return JsonResponse({"resole": request.POST.get('name')})


# 编辑部门经理
@login_required(login_url='/login/')
@csrf_exempt
def department_admin(request):
    if request.is_ajax():
        user = User.objects.get(id=request.POST.get('id'))
        is_admin = request.POST.get('is_admin')
        role_user = Role.objects.get(id=1)
        role_admin = Role.objects.get(id=2)
        if is_admin == '1':
            user.is_admin = True
            user.role = role_admin
        elif is_admin == '0':
            user.is_admin = False
            user.role = role_user
        user.save()
        return JsonResponse({"resole": 0})


@login_required(login_url='/login/')
@csrf_exempt
def active(request):
    if request.is_ajax():
        user = User.objects.get(id=request.POST.get('id'))
        if request.POST.get('type') == '0':
            user.is_active = False
            user.save()
        elif request.POST.get('type') == '1':
            user.is_active = True
            user.save()
        return JsonResponse({"resole": 0})
