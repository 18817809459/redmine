
from django.forms import forms,ModelForm


def create_model_form(request,admin_class):

    def __new__(cls,*args,**kwargs):
        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form_contral'
        return ModelForm.__new__(cls)
    class Meta:
        model = admin_class.model
        fields = "__all__"

    attrs = {'Meta':Meta}
    _model_form_class = type("DynamicModelForm",(ModelForm,),{'Meta':Meta})
    setattr(_model_form_class,'__new__',__new__)

    return _model_form_class


