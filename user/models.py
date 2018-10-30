from django.db import models
from django.contrib.auth.models import AbstractUser,Permission,Group
# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=30,unique=True)
    permission = models.ManyToManyField(Permission)
    active = models.BooleanField(default=True)
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = "角色"

class Department(models.Model):
    '''部门'''
    department_name = models.CharField(max_length=30, unique=True, verbose_name='名称')
    # active = models.BooleanField(default=True)
    # spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.department_name

    class Meta:
        verbose_name = "部门"
        verbose_name_plural = "部门"

class User(AbstractUser):
    phone = models.CharField(unique=True,max_length=20)
    head = models.ImageField(upload_to="image/user/%Y/%m/%d/",default="image/user/mo.jpg")
    gender_choice = (
        (0, "男"),
        (1, "女"),
    )
    gender = models.SmallIntegerField(choices=gender_choice,default=0)
    entry_time = models.DateField(null=True, blank=True)
    duty = models.CharField(max_length=20, null=True, blank=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    first_type = models.CharField(max_length=100, null=True, blank=True)
    two_type = models.CharField(max_length=100, null=True, blank=True)
    three_type = models.CharField(max_length=100, null=True, blank=True)
    four_type = models.CharField(max_length=100, null=True, blank=True)
    role = models.ForeignKey(Role,on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.first_name

    class Meta(AbstractUser.Meta):
        unique_together = ('email',)

class SessionUser(models.Model):
    session = models.CharField(max_length=100,unique=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)


class Csrf(models.Model):
    session = models.CharField(max_length=100, unique=True)
    csrf = models.CharField(max_length=100)