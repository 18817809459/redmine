from user import models

def department():
    list = []
    num1 = models.User.objects.filter(is_active=True).count()
    user_a = {'name':"全部",'id':'','count':num1}
    list.append(user_a)
    departments = models.Department.objects.all()
    for department in departments:
        num = models.User.objects.filter(department=department,is_active=True).count()
        user_count = {'name': department.department_name, 'id': department.id, 'count': num}
        list.append(user_count)
    return list