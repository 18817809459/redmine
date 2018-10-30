from django import forms
from user.models import User, Department
import re


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['head', 'first_name', 'last_name', 'gender', 'entry_time', 'department', 'duty', 'phone', 'email']

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        p = re.compile('^((\d{3,4}-)?\d{7,8})$|(1[3-9][0-9]{9})')
        if p.match(phone):
            return phone
        else:
            raise forms.ValidationError('手机号码非法', code='phone_inval')

    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            return email
        else:
            raise forms.ValidationError('邮箱不能为空', code='email_inval')


class UF(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'phone', 'email', 'head']


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'
