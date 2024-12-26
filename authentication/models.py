from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Permission
# from phonenumber_field.modelfields import PhoneNumberField

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)

    def create_master_admin(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

    def create_super_admin(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superadmin', True)
        return self.create_user(username, password, **extra_fields)

    def create_admin(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    head_office = models.ForeignKey('HeadOffice', on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey('Branches', on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True
        if self.is_superadmin:
            return RolePermission.objects.filter(role='super_admin', permission=perm, enabled=True).exists()
        if self.is_admin:
            return RolePermission.objects.filter(role='admin', permission=perm, enabled=True).exists()
        return False

    def has_module_perms(self, app_label):
        return self.is_superuser
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    
#----------------------------------------------------------------------------------------------------------------------------------------

from django.core.exceptions import ValidationError
import re



def validate_phone_number(value):
   
    phone_regex = re.compile(r'^\+?([1-9]\d{0,3})\d{6,12}$')
    
    if not phone_regex.match(value):
        raise ValidationError(
            "Please enter a valid international phone number with country code. "
            "Format: +[country code][number] (e.g., +911234567890)"
        )
class Client(models.Model):
    prefix = models.CharField(max_length=10, unique=True)
    # user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    client_name = models.CharField(max_length=255)
    client_address = models.CharField(max_length=255)
    client_contact = models.CharField(max_length=15,validators=[validate_phone_number],unique=True,help_text="Enter phone number with country code (e.g., +911234567890)")
    is_head_office = models.BooleanField(default=False)
    is_branch = models.BooleanField(default=False)
    logo_image=models.ImageField(upload_to='offiec_logo')
    created_at=models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f" {self.prefix}"
    
#---------------------------------------------------------------------------------------------------------------------------------------

class HeadOffice(models.Model):
    prefix = models.CharField(max_length=10, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15,validators=[validate_phone_number])
    
    is_branch = models.BooleanField(default=False)
    logo_image=models.ImageField(upload_to='offiec_logo')
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.prefix}"

#------------------------------------------------------------------------------------------------------------------------------------------    

class Branches(models.Model):
    prefix = models.CharField(max_length=10, unique=True)
    head_office = models.ForeignKey(HeadOffice, on_delete=models.CASCADE,null=True,blank=True,related_name='branches')
    branch_name = models.CharField(max_length=255)
    branch_address = models.CharField(max_length=255)
    branch_contact_number = models.CharField(max_length=15,validators=[validate_phone_number])
    
    logo_image=models.ImageField(upload_to='offiec_logo')
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.prefix}"
 

#----------------------------------------------------------------------------------------------------------------------------------------   
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse
from django.conf import settings
import os

class Departments(models.Model):
    dpt_name=models.CharField(max_length=255,unique=True)
    branch=models.ForeignKey(Branches,on_delete=models.CASCADE)
    qr_code = models.ImageField(upload_to='department_qr_codes/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.qr_code:
            # Generate QR code when department is created
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            # Add your data to QR code (e.g., department detail URL)
            qr.add_data(f'/department/{self.id}/')
            qr.make(fit=True)

            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            filename = f'department_{self.id}_qr.png'
            
            # Save QR code image
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            filename = f'department_{self.id}_qr.png'
            self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        
        super().save(*args, **kwargs)
    
    
    
    def __str__(self):
        return self.dpt_name




class CommissionMembers(models.Model):
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=200)  # Fixed typo here
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, validators=[validate_phone_number])  # Correctly referenced validator
    departments = models.ManyToManyField(Departments)

    def __str__(self):
        return self.name

# ChairMan Model
class ChairMan(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, validators=[validate_phone_number])  # Correctly referenced validator

    def __str__(self):
        return self.name
    
    
    






class RolePermission(models.Model):
    ROLE_CHOICES = [
    ('super_admin', 'Super Admin'),
    ('admin', 'Admin'),
    
]

    PERMISSION_CHOICES = [
    ('add_branch', 'Create Branch'),
        ('list_branch', 'List Branch'),
        ('edit_branch', 'Edit Branch'),
        ('delete_branch', 'Delete Branch'),
        ('create_admin', 'Create Admin'),
        ('create_head_office', 'Create Head Office'),
        ('list_head_office', 'List Head Office'),
        ('edit_head_office', 'Edit Head Office'),
        ('delete_head_office', 'Delete Head Office'),
        ('view_reports', 'View Reports'),
        ('add_client', 'Add Client'),
        ('edit_client', 'Edit Client'),
        ('delete_client', 'Delete Client'),
        ('list_client', 'List Client'),
]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES)
    enabled = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'permission')

    def __str__(self):
        return f"{self.get_role_display()} - {self.get_permission_display()}"
    
    
    
    
    

