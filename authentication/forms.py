from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser,HeadOffice,Client,Branches
from django.contrib.auth.forms import AuthenticationForm
from django.db import models

from phonenumbers import parse, is_valid_number, NumberParseException


class MasterAdminCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user




from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
class SuperAdminCreationForm(UserCreationForm):
    head_office = forms.ModelChoiceField(
        queryset=HeadOffice.objects.all(),
        required=True,
        label="Head Office",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'head_office')
    def clean(self):
        cleaned_data = super().clean()
        head_office = cleaned_data.get('head_office')

        if head_office:
            existing_user = CustomUser.objects.filter(head_office=head_office, is_superadmin=True).first()
            if existing_user:
                raise ValidationError(f"A user already exists for the head office '{head_office}'. "
                                      f"Username: {existing_user.username}")

        return cleaned_data
        

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_superadmin = True
        if commit:
            user.save()
            head_office = self.cleaned_data['head_office']
            user.head_office = head_office
            user.save()
        return user    
        



class AdminCreationForm(UserCreationForm):
    branch = forms.ModelChoiceField(queryset=Branches.objects.all(), required=True,
                                    widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'branch')
        
    def clean(self):
        cleaned_data = super().clean()
        branch = cleaned_data.get('branch')

        if branch:
            existing_user = CustomUser.objects.filter(branch=branch, is_admin=True).first()
            if existing_user:
                raise ValidationError(f"A user already exists for the branch office '{branch}'. "
                                      f"Username: {existing_user.username}")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_admin = True  # Always set is_admin to True
        if commit:
            user.save()
            user.branch = self.cleaned_data['branch']
            user.save()
        return user
    
    
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError('Invalid username or password')
        return cleaned_data
    





from .models import RolePermission

class RolePermissionForm(forms.ModelForm):
    class Meta:
        model=RolePermission
        fields='__all__'
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'permission': forms.Select(attrs={'class': 'form-control'}),
            'enabled':forms.CheckboxInput(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        permission = cleaned_data.get('permission')
        # Add custom validation here if needed
        return cleaned_data
    


from django import forms
from .models import Client, HeadOffice, Branches

from .models import validate_phone_number


class ClientForm(forms.ModelForm):
    client_contact = forms.CharField(
        validators=[validate_phone_number],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Client
        fields = ['prefix', 'client_name', 'client_address', 'client_contact', 'is_head_office', 'is_branch','logo_image']
        widgets = {
            'prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'client_name': forms.TextInput(attrs={'class': 'form-control'}),
            'client_address': forms.Textarea(attrs={'class': 'form-control'}),
            'client_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'is_head_office': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_branch': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'logo_image':forms.FileInput(attrs={'class':'form-control'})

        }

  
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ClientForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ClientForm, self).save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance
    

class HeadOfficeForm(forms.ModelForm):

    class Meta:
        model = HeadOffice
        fields = '__all__'
        widgets = {
            'prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_branch': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'logo_image':forms.FileInput(attrs={'class':'form-control'})
        }
    

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branches
        fields = '__all__'
        widgets = {
            'prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'head_office': forms.Select(attrs={'class': 'form-control'}),
            'branch_name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch_address': forms.Textarea(attrs={'class': 'form-control'}),
            'branch_contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'logo_image':forms.FileInput(attrs={'class':'form-control'})
        }
    
    
from .models import Departments

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Departments
        fields = ['dpt_name', 'branch']
        widgets = {
            'dpt_name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            
        }
        
        
from django import forms
from .models import CommissionMembers, ChairMan

class CommissionMembersForm(forms.ModelForm):
    class Meta:
        model = CommissionMembers
        fields = ['name', 'designation', 'email', 'phone_number', 'departments']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter name'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter designation'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'departments': forms.CheckboxSelectMultiple()
        }

class ChairManForm(forms.ModelForm):
    class Meta:
        model = ChairMan
        fields = ['name', 'email', 'phone_number']  # Add other fields
