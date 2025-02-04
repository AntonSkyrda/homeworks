from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class CourseFilterForm(forms.Form):
    teacher = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    tags = forms.CharField(required=False, help_text="Enter tags separated by coma")
    start_date = forms.DateField(required=False, widget=forms.SelectDateWidget)
