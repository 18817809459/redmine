from django.db import models
from user.models import User, Department


# Create your models here.
class File(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, blank=True)
    task_discuss = models.ForeignKey('TaskDiscuss', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='file/%Y/%m/%d/')
    postfix = models.CharField(max_length=20, null=True, blank=True)
    existent = models.BooleanField(default=False)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.NullBooleanField()
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    project_discuss = models.ForeignKey('ProjectDiscuss', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "文件管理"
        verbose_name_plural = "文件管理"


class ProjectType(models.Model):
    '''项目类型'''
    name = models.CharField(max_length=30, unique=True, verbose_name='名称')
    description = models.TextField(max_length=100, verbose_name='描述')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属部门')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "项目类型"
        verbose_name_plural = "项目类型"


class ProjectFlow(models.Model):
    '''项目流程'''
    flow_name = models.CharField(max_length=30, unique=True, verbose_name="名称")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="所属部门")
    flow_description = models.TextField(max_length=200, verbose_name="描述")
    is_active = models.BooleanField(default=True)
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.flow_name

    class Meta:
        verbose_name = "项目流程"
        verbose_name_plural = "项目流程"


class FlowNode(models.Model):
    '''流程节点'''
    node_name = models.CharField(max_length=30)
    flow = models.ForeignKey(ProjectFlow, on_delete=models.CASCADE)
    num = models.SmallIntegerField()
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.node_name

    class Meta:
        verbose_name = "流程节点"
        verbose_name_plural = "流程节点"


class NodeNode(models.Model):
    '''流程小节点'''
    name = models.CharField(max_length=30)
    flow = models.ForeignKey(FlowNode, on_delete=models.CASCADE)
    num = models.SmallIntegerField()
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "流程小节点"
        verbose_name_plural = "流程小节点"


class Project(models.Model):
    '''项目'''
    project_name = models.CharField(max_length=30, unique=True)
    contract_no = models.CharField(null=True, blank=True, max_length=30)
    priject_description = models.TextField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    tag_choice = (
        (0, "内部"),
        (1, "外部"),
    )
    tag = models.SmallIntegerField(choices=tag_choice)
    project_type = models.ForeignKey(ProjectType, on_delete=models.CASCADE)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    examined_choice = (
        (0, "部门经理审批"),
        (1, "管理员审批"),
        (2, "审批完成"),
        (3, "审核失败"),
    )
    examined = models.SmallIntegerField(choices=examined_choice)
    node = models.ForeignKey(FlowNode, on_delete=models.CASCADE)
    flow = models.ForeignKey(ProjectFlow, on_delete=models.CASCADE)
    status_choice = (
        (0, "审核中"),
        (1, "执行中"),
        (2, "已延期"),
        (3, "已结束"),
        (4, "已搁置"),
        (5, "已暂停"),
    )
    status = models.SmallIntegerField(choices=status_choice)
    delay_choice = (
        (0, "未申请"),
        (1, "待审核"),
        (2, "审核成功"),
        (3, "审核失败"),
    )
    delay_status = models.SmallIntegerField(choices=delay_choice)
    node_node = models.ForeignKey(NodeNode, on_delete=models.CASCADE, null=True, blank=True)
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    alert_time = models.DateTimeField(null=True, blank=True)
    supension_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.project_name

    class Meta:
        verbose_name = "项目"
        verbose_name_plural = "项目"


class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class ProjectLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.TextField()
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)


class ProjectRecord(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    record = models.TextField()
    time = models.DateField()
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)


class Examine(models.Model):
    '''项目审核'''
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_user')
    examined_choice = (
        (0, "部门经理审批"),
        (1, "管理员审批"),
    )
    examine = models.SmallIntegerField(choices=examined_choice)
    is_pass = models.NullBooleanField()
    examine_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='examine_user', null=True, blank=True)
    description = models.TextField(max_length=200, null=True, blank=True)
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "项目审核"
        verbose_name_plural = "项目审核"


class ProjectNode(models.Model):
    '''项目节点'''
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    time = models.DateTimeField()
    number = models.BigIntegerField()
    unit = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    active = models.NullBooleanField()
    order = models.BigIntegerField(null=True, blank=True)
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    node = models.ForeignKey(FlowNode, on_delete=models.CASCADE, null=True, blank=True)
    node_node = models.ForeignKey(NodeNode, on_delete=models.CASCADE, null=True, blank=True)
    node_alert_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "项目节点"
        verbose_name_plural = "项目节点"


class ProjectNodeFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    project_node = models.ForeignKey(ProjectNode, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class ProjectUser(models.Model):
    '''项目成员'''
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_host = models.BooleanField(default=False)
    active = models.NullBooleanField()
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "项目成员"
        verbose_name_plural = "项目成员"


class ProjectDiscuss(models.Model):
    '''任务讨论'''
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    discuss = models.TextField()
    order = models.BigIntegerField()
    active = models.NullBooleanField()
    created_user = models.ForeignKey(User, on_delete=models.CASCADE)
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class ProjectDiscussFile(models.Model):
    project_discuss = models.ForeignKey(ProjectDiscuss, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class TaskType(models.Model):
    '''任务类型'''
    name = models.CharField(max_length=30, verbose_name='名称')
    description = models.TextField(max_length=100, verbose_name='描述')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属部门')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "任务类型"
        verbose_name_plural = "任务类型"
        unique_together = ('name', 'department',)


class Task(models.Model):
    '''任务'''
    name = models.CharField(max_length=30, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    require = models.CharField(max_length=100)
    description = models.TextField(max_length=200)
    end_time = models.DateTimeField()
    task_type = models.ForeignKey(TaskType, on_delete=models.CASCADE)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE)
    status_choice = (
        (0, "待执行"),
        (1, "执行中"),
        (2, "已延期"),
        (3, "已结束"),
        (4, "已搁置"),
        (5, "已暂停"),
    )
    status = models.SmallIntegerField(choices=status_choice)
    delay_choice = (
        (0, "未申请"),
        (1, "待审核"),
        (2, "审核成功"),
        (3, "审核失败"),
    )
    delay_status = models.SmallIntegerField(choices=delay_choice, default=0)
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    alert_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "任务"
        verbose_name_plural = "任务"


class TaskUser(models.Model):
    '''任务指派'''
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_host = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "任务指派"
        verbose_name_plural = "任务指派"


class TaskFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class TaskLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    description = models.TextField()
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)


class TaskDiscuss(models.Model):
    '''任务讨论'''
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    discuss = models.TextField()
    order = models.BigIntegerField()
    active = models.NullBooleanField()
    created_user = models.ForeignKey(User, on_delete=models.CASCADE)
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class TaskDiscussFile(models.Model):
    task_discuss = models.ForeignKey(TaskDiscuss, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class Delay(models.Model):
    '''延期申请'''
    type = models.CharField(max_length=20)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    project_node = models.ForeignKey(ProjectNode, on_delete=models.CASCADE, null=True, blank=True)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="create", )
    reason = models.TextField(null=True, blank=True)
    time = models.DateTimeField()
    is_pass = models.NullBooleanField()
    description = models.TextField(max_length=200, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leading", null=True, blank=True)
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "延期申请"
        verbose_name_plural = "延期申请"


class History(models.Model):
    type = models.CharField(max_length=20)
    old = models.TextField(null=True, blank=True)
    new = models.TextField(null=True, blank=True)
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)


class ContributionType(models.Model):
    '''贡献类型'''
    name = models.CharField(max_length=30, unique=True, verbose_name='名称')
    description = models.TextField(max_length=100, verbose_name='描述')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属部门')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "贡献类型"
        verbose_name_plural = "贡献类型"


class Contribution(models.Model):
    '''贡献'''
    name = models.CharField(max_length=100, unique=True, verbose_name="贡献名称")
    type = models.ForeignKey(ContributionType, on_delete=models.CASCADE, verbose_name="贡献类型")
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="create_user", verbose_name="创建人")
    description = models.TextField(verbose_name="内容")
    user = models.ManyToManyField(User, related_name="gave", verbose_name="指定人")
    active = models.NullBooleanField()
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "贡献"
        verbose_name_plural = "贡献"


class Notice(models.Model):
    notice = models.CharField(max_length=300)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE)
    type_choices = (
        (0, "项目"),
        (1, "任务"),
        (2, "延期"),
        (3, "系统"),
        (4, "其他"),
    )
    type = models.SmallIntegerField(choices=type_choices)
    read = models.BooleanField(default=False)
    active = models.NullBooleanField(default=True)
    spare = models.CharField(max_length=100, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
