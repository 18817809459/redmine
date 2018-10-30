from django.shortcuts import render,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from king_ad.utils import table_filter,table_sort,table_search
from king_ad import king_ad
from king_ad.forms import create_model_form
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from project import models as project
from user import models as us


# Create your views here.
def index_obj(request,app_name,table_name):
    admin_class = king_ad.enabled_admins[app_name][table_name]
    object_list, filter_condtions = table_filter(request, admin_class)
    object_list = table_search(request, admin_class, object_list)
    object_list, orderby_key = table_sort(request, admin_class, object_list)
    return admin_class, object_list, filter_condtions, orderby_key

def obj(request,app_name,table_name,ids=None,department=0):
    admin_class = king_ad.enabled_admins[app_name][table_name]
    object_list, filter_condtions = table_filter(request, admin_class)
    if ids:
        object_list = object_list.filter(id__in=ids)
    if department != 0:
        object_list = object_list.filter(department_id=department)
    object_list = table_search(request, admin_class, object_list)
    object_list, orderby_key = table_sort(request, admin_class, object_list)
    paginator = Paginator(object_list, admin_class.list_per_page)
    page = request.GET.get('page')
    try:
        query_sets = paginator.page(page)
    except PageNotAnInteger:
        query_sets = paginator.page(1)
    except EmptyPage:
        query_sets = paginator.page(paginator.num_pages)
    return admin_class,query_sets,filter_condtions,orderby_key

def index(request):
    return render(request, "king_ad/table_index.html",{'table_list':king_ad.enabled_admins})

@login_required
def display_table_objs(request,app_name,table_name):
    ids = []
    department = 0
    if request.user.is_admin:
        department = request.user.department_id
    admin_class, query_sets, filter_condtions, orderby_key = obj(request, app_name, table_name,ids,department)
    return render(request, 'project/project_objs.html', {'admin_class': admin_class,
                                                         'query_sets': query_sets,
                                                         'filter_condtions': filter_condtions,
                                                         'orderby_key': orderby_key,
                                                         'precious_orderby': request.GET.get("o", ''),
                                                         'search_text': request.GET.get('_q', ''),
                                                         'table_name':table_name})
@login_required
def table_objs_change(request,app_name,table_name,id):
    admin_class = king_ad.enabled_admins[app_name][table_name]
    model_form_class = create_model_form(request,admin_class)
    obj = admin_class.model.objects.get(id=id)

    if request.method == "POST":
        form_obj = model_form_class(request.POST,instance=obj)
        csrf = us.Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if form_obj.is_valid():
                form_obj.save()
                if table_name == 'department':
                    return redirect(reverse('department_user'))
                return redirect(reverse('table_objs',kwargs={'app_name': app_name,'table_name':table_name}))
    else:
        form_obj = model_form_class(instance=obj)
    return render(request,'king_ad/table_obj_change.html',{'model_form':form_obj,'admin_class':admin_class,
                                                           'app_name':app_name,'table_name':table_name})

@login_required
def table_obj_add(request,app_name,table_name):
    admin_class = king_ad.enabled_admins[app_name][table_name]
    model_form_class = create_model_form(request, admin_class)

    if request.method == "POST":
        csrf = us.Csrf.objects.get(session=request.session.session_key)
        if csrf.csrf != request.POST.get('csrfmiddlewaretoken'):
            csrf.csrf = request.POST.get('csrfmiddlewaretoken')
            csrf.save()
            if table_name == "tasktype" and request.POST.get('department') == "all":
                departments = us.Department.objects.all()
                for department in departments:
                    project.TaskType.objects.create(name=request.POST.get('name'),
                                                    description=request.POST.get('description'),
                                                    department=department)
                return redirect(request.path.replace('/add/', "/"))
            else:
                form_obj = model_form_class(request.POST)
                if form_obj.is_valid():
                    form_obj.save()
                    if table_name == 'department':
                        return redirect(reverse('department_user'))
                    return redirect(request.path.replace('/add/',"/"))
    else:
        form_obj = model_form_class()
    return render(request, 'king_ad/table_obj_add.html', {'model_form': form_obj,'admin_class':admin_class,
                                                          'app_name':app_name,'table_name':table_name})

@login_required
def table_obj_delete(request,app_name,table_name,id):
    admin_class = king_ad.enabled_admins[app_name][table_name]

    obj = admin_class.model.objects.get(id=id)
    if admin_class.readonly_table:
        errors = {"readonly_table": "table is readonly ,obj [%s] cannot be deleted" % obj}
    else:
        errors = {}
    if request.method == "POST":
        if not admin_class.readonly_table:
            obj.delete()
            return redirect("/admin/%s/%s/" %(app_name,table_name))

    return render(request,'king_ad/table_obj_delete.html',{'obj':obj,
                                                              'admin_class':admin_class,
                                                              'app_name': app_name,
                                                              'table_name': table_name,
                                                              'errors':errors
                                                              })