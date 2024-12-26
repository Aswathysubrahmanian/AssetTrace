from django import forms
from .models import AssetType, AssetData,Asset_movement_data,Depreciation
from authentication.models import Branches,HeadOffice

class AssetTypeForm(forms.ModelForm):
    class Meta:
        model = AssetType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

from django.core.exceptions import ValidationError
from django.forms import FileField
from django.utils.translation import gettext_lazy as _
import os


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update({'class': 'form-control', 'multiple': True})
        super().__init__(attrs)

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        # Call the parent clean method
        single_file_clean = super().clean
        
        # List of accepted image file extensions
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

        # Validate files in data
        if isinstance(data, (list, tuple)):
            result = [self.validate_image_file(single_file_clean(d, initial), allowed_extensions) for d in data]
        else:
            result = self.validate_image_file(single_file_clean(data, initial), allowed_extensions)
        return result
    def validate_image_file(self, file, allowed_extensions):
        # Check file extension
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in allowed_extensions:
            raise ValidationError(
                _('Invalid file type: %(ext)s. Only image files are allowed.'),
                params={'ext': ext},
            )
        return file

# class AssetDataForm(forms.ModelForm):
#     images = MultipleFileField(label='Upload Image (Upload bill or warranty information or this asset related valid documents) *',  # Changed label
#         required=False,
        
#                                )
    
#     class Meta:
#         model = AssetData
#         fields = '__all__'
#         exclude = ['custom_fields','is_auto_generated']
#         widgets = {
#             'asset_code': forms.TextInput(attrs={'class': 'form-control'}),
#             'asset_type': forms.Select(attrs={'class': 'form-control'}),
#             'office': forms.Select(attrs={'class': 'form-control', 'id': 'id_office'}),
#             'branch': forms.Select(attrs={'class': 'form-control', 'id': 'id_branch'}),
#             'department':forms.Select(attrs={'class':'form-control'}),
#             'asset_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'model': forms.TextInput(attrs={'class': 'form-control'}),
#             'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
#             'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'warranty_info': forms.TextInput(attrs={'class': 'form-control'}),
#             'price': forms.NumberInput(attrs={'class': 'form-control'}),
            
#         }
#     custom_fields = forms.CharField(widget=forms.HiddenInput(), required=False)

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.custom_fields = []
#         for field_name, field in self.fields.items():
#             if field.required:
#                 field.label = f'{field.label} *'

#         self.fields['branch'].queryset = Branches.objects.none()

#         if 'asset-office' in self.data:
#             office_id = int(self.data.get('asset-office'))
#             self.fields['branch'].queryset = Branches.objects.filter(head_office_id=office_id).order_by('branch_name')
#         elif self.instance.pk:
#             self.fields['branch'].queryset = self.instance.office.branches.order_by('branch_name')
            
            
   
class AssetDataForm(forms.ModelForm):
    image=MultipleFileField()

    bill_file=MultipleFileField(label='Upload Image (Upload bill or warranty information or this asset related valid documents)', required=False)

    class Meta:
        model = AssetData
        fields = '__all__'
        exclude = ['custom_fields', 'is_auto_generated']
        widgets = {
            'asset_code': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_type': forms.Select(attrs={'class': 'form-control'}),
            'office': forms.Select(attrs={'class': 'form-control', 'id': 'id_office'}),
            'branch': forms.Select(attrs={'class': 'form-control', 'id': 'id_branch'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'asset_name': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_info': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'custodian': forms.TextInput(attrs={'class': 'form-control'}),
        }
    custom_fields = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
       
        super().__init__(*args, **kwargs)
        
        # Set office and branch based on user
        

        self.custom_fields = []
        for field_name, field in self.fields.items():
            if field.required:
                field.label = f'{field.label} *'

        # self.fields['branch'].queryset = Branches.objects.none()

        # if 'asset-office' in self.data:
        #     office_id = int(self.data.get('asset-office'))
        #     self.fields['branch'].queryset = Branches.objects.filter(head_office_id=office_id).order_by('branch_name')
        # elif self.instance.pk:
        #     self.fields['branch'].queryset = self.instance.office.branches.order_by('branch_name')
        self.fields['branch'].queryset = Branches.objects.none()

        # If we have form data
        if 'office' in self.data:
            try:
                office_id = int(self.data.get('office'))
                self.fields['branch'].queryset = Branches.objects.filter(
                    head_office_id=office_id).order_by('branch_name')
            except (ValueError, TypeError):
                pass
        # If we're editing an existing instance
        elif self.instance.pk and self.instance.office:
            self.fields['branch'].queryset = Branches.objects.filter(
                head_office=self.instance.office).order_by('branch_name')


from .models import AssetImage 
class ImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image')    
    class Meta:
        model = AssetImage
        fields = ('image', )
        widgets={
            'image':forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

class AssetMovementForm(forms.ModelForm):
    class Meta:
        model = Asset_movement_data
        fields = '__all__'
        widgets = {
            'asset': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'from_branch': forms.Select(attrs={'class': 'form-control'}),
            'to_branch': forms.Select(attrs={'class': 'form-control'}),
            'movement_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'return_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['from_branch'].widget.attrs['readonly'] = True
        
        
class DepreciationForm(forms.ModelForm):
    class Meta:
        model = Depreciation
        fields = ['useful_life', 'depreciation_method', 'salvage_value']
        widgets = {
            'asset': forms.Select(attrs={'disabled': 'disabled','class':'form-control'}),
            'useful_life':forms.TextInput(attrs={'class':'form-control'}),
            'depreciation_method':forms.Select(attrs={'class':'form-control'}),
            'salvage_value':forms.TextInput(attrs={'class':'form-control'})
            
        }

    def __init__(self, *args, **kwargs):
        asset = kwargs.pop('asset', None)
        super().__init__(*args, **kwargs)
        
            
        self.fields['salvage_value'].required = False


    

  




import json
# class CustomDepreciationForm(forms.ModelForm):
#     class Meta:
#         model = Depreciation
#         fields = ['useful_life']
#         widgets = {
            
#             'useful_life': forms.NumberInput(attrs={'class': 'form-control'}),
#         }

#     custom_percentages = forms.CharField(widget=forms.HiddenInput(), required=False)

#     def __init__(self, *args, **kwargs):
#         asset = kwargs.pop('asset', None)
#         super().__init__(*args, **kwargs)
        

#     def clean_custom_percentages(self):
#         data = self.cleaned_data['custom_percentages']
#         try:
#             parsed_data = json.loads(data)
#             if not isinstance(parsed_data, list):
#                 raise forms.ValidationError("Custom percentages must be a list of year-percentage pairs.")
#             return parsed_data
#         except json.JSONDecodeError:
#             raise forms.ValidationError("Invalid JSON format for custom percentages.")


class CustomDepreciationForm(forms.ModelForm):
    custom_percentages = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Depreciation
        fields = ['useful_life']
        widgets = {
            'useful_life': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        asset = kwargs.pop('asset', None)
        super().__init__(*args, **kwargs)

    def clean_custom_percentages(self):
        data = self.cleaned_data['custom_percentages']
        try:
            parsed_data = json.loads(data)
            if not isinstance(parsed_data, list):
                raise forms.ValidationError("Custom percentages must be a list of year-percentage pairs.")
            # Ensure each item in the list is a dictionary with 'year' and 'percentage' keys
            for item in parsed_data:
                if not isinstance(item, dict) or 'year' not in item or 'percentage' not in item:
                    raise forms.ValidationError("Each item must be a dictionary with 'year' and 'percentage' keys.")
            return parsed_data
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON format for custom percentages.")
        
        
        

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Upload Excel File')