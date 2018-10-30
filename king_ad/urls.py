

from django.urls import path
from king_ad import views

urlpatterns = [
    path(r'list',views.index,name="table_index"),
    path(r'<app_name>/<table_name>/',views.display_table_objs,name="table_objs"),
    path(r'<app_name>/<table_name>/<id>/change/', views.table_objs_change, name="table_obj_change"),
    path(r'<app_name>/<table_name>/<id>/delete/', views.table_obj_delete, name="obj_delete"),
    path(r'<app_name>/<table_name>/add/',views.table_obj_add,name="table_obj_add"),
]
