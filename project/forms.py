from django import forms
from project import models


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = '__all__'
        exclude = ['is_close', 'node', 'examined', 'created_user', 'alert_time', 'node_node','spare']
        labels = {'project_name': "项目名称", 'project_type': "项目类型", 'contract_no': "合同编号", 'flow': "选择流程",
                  'department': "所属部门", 'priject_description': "描述", 'start_time': "开始时间", 'end_time': "结束时间"}
        error_messages = {
            'contract_no': {
                'unique': "合同编号错误",
            },
        }


class ProjectUserForm(forms.ModelForm):
    class Meta:
        model = models.ProjectUser
        fields = '__all__'
        exclude = ['project', 'host']
        labels = {'user': "托付"}


class ProjectFlowForm(forms.ModelForm):
    class Meta:
        model = models.ProjectFlow
        fields = '__all__'
        labels = {'flow_name': "名称", 'department': "所属部门", 'flow_description': "描述"}


class FlowNodeForm(forms.ModelForm):
    class Meta:
        model = models.FlowNode
        fields = ['node_name']
        labels = {'node_name': "名称"}


class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = '__all__'
        exclude = ['created_user', 'is_close','spare']
        labels = {'name': "任务名称", 'project': "所属项目", 'require': "任务要求", 'description': "任务描述",
                  'end_time': "交付时间", 'task_type': "任务类型"}


class TaskUserForm(forms.ModelForm):
    class Meta:
        model = models.TaskUser
        fields = ['user']
        labels = {'user': "任务托付"}


class TaskFileForm(forms.ModelForm):
    class Meta:
        model = models.TaskFile
        fields = ['file']
        labels = {'file': "附件添加"}


class DelayForm(forms.ModelForm):
    class Meta:
        model = models.Delay
        fields = '__all__'
        exclude = ['created_user', 'is_pass', 'user', 'description']
        labels = {'reason': "延期理由", 'time': "延期时间", 'project_node': "项目节点"}


class ExamineForm(forms.ModelForm):
    class Meta:
        model = models.Examine
        fields = ['is_pass', 'description']


class ContributionForm(forms.ModelForm):
    class Meta:
        model = models.Contribution
        fields = '__all__'
        exclude = ['created_user', 'created_time', 'user']
