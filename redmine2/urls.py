"""redmine2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include,re_path
from redmine2 import views as redmine
from user import views as user
from django.views.static import serve
from django.conf import settings
from project import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'static/<path>.*', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}, name='upload'),
    path(r'king_ad/', include('king_ad.urls')),
    path(r'login/', user.login, name='login'),
    path(r'logout/', user.logout),
    path(r'', redmine.index, name='index'),
    path(r'<int:id>/change/', views.project_edit),
    path(r'<int:id>/', views.project_show),
    path(r'project/', include('project.urls')),
    path(r'auth/user/', user.user_obj, name='auth_user'),
    path(r'role/', user.role_obj, name='role'),
    path(r'role/add/', user.role_add, name='user_add'),
    path(r'role/<int:id>/change/', user.role_permission),
    path(r'personal/', user.personal, ),
    path(r'active/api/', user.active),
    path(r'auth/user/add/', user.user_add, name='auth_user_add'),
    path(r'auth/user/<int:id>/change/', user.user_edit, name='auth_user_change'),
    path(r'department/', user.depertment, name='department_user'),
    path(r'department/add/', user.department_add, name='department_add'),
    path(r'department/admin/', user.department_admin),
    path(r'department/<int:id>/change/', user.department_edit, name='department_edit'),
    # path(r'echo/', redmine.echo),
    path(r'400/', redmine.error_400),
    path(r'403/', redmine.error_403),
    path(r'404/', redmine.error_404),
    path(r'500/', redmine.error_500),
    path(r'503/', redmine.error_503), ]
# ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = redmine.error_404
handler500 = redmine.error_500
