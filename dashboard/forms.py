from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import SetPasswordForm
from .models import CustomUser
import datetime



from django import forms
from .models import Department

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Department Name'})
        }

class DepartmentUploadForm(forms.Form):
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label="Upload CSV File"
    )




from django import forms
from .models import CustomUser, Department

class CustomUserSimpleForm(forms.ModelForm):
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all().order_by("name"),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'branch_name', 'branch_code','departments', 'user_role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add a fake "All" choice via Select2 placeholder hack
        self.fields['departments'].widget.attrs.update({
            'data-placeholder': 'Select Departments or All',
        })
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_departments(self):
        departments = self.cleaned_data.get('departments')
        # If user selected nothing OR we want "All", assign all
        if not departments:
            return Department.objects.all()
        return departments



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})





from django import forms
from .models import BankMaster

class BankMasterForm(forms.ModelForm):
    class Meta:
        model = BankMaster
        fields = ['branch_code', 'branch_name']
        widgets = {
            'branch_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Branch Code'}),
            'branch_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Branch Name'}),
        }


class BankUploadForm(forms.Form):
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label="Upload CSV File"
    )



class CustomPasswordChangeForm(SetPasswordForm):
    # You can customize labels, widgets, etc. here if needed.
    old_password = forms.CharField(
        label="Old Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
