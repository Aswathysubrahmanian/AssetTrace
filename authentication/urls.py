from django.urls import path
from . import views



urlpatterns = [
    path('create-master-admin/', views.create_master_admin, name='create_master_admin'),
    path('create-super-admin/', views.create_super_admin, name='create_super_admin'),
    path('create-admin/', views.create_admin, name='create_admin'),
    path('master-dashboard/',views.masterAdminDashboard,name='master_admin_dashboard'),
    path('head-office-dashboard/',views.superAdminDashboard,name='super_admin_dashboard'),
    path('branch-dashboard/',views.AdminDashboard,name='branch_dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('',views.login_view,name='login'),
    path('login_for_asset/<int:asset_id>/',views.login_view_for_asset,name='login_for_asset'),
    path('logout/',views.logout_view,name='logout'),
    path('add-head-office/',views.addHeadofficeView,name='add_head_office'),
    path('list-head-office/',views.listofHeadoffice,name='list_head_office'),
    path('add-client/',views.create_client,name='add_client'),
    path('list-of-client/',views.listofclients,name='list_client'),
    path('edit_client/<int:pk>/', views.edit_client, name='edit_client'),
    path('delete_client/<int:pk>/', views.delete_client, name='delete_client'),
    path('add-branches/',views.addBranches,name='add_branches'),
    path('list-of-branches/',views.listofBranches,name='branch_list'),
    path('manage-permissions/', views.manage_permissions, name='manage_permissions'),
    path('delete-permission/<int:pk>/', views.delete_permission, name='delete_permission'),
    path('profile/',views.profile,name='profile'),
    path('edit_head_office/<int:id>/', views.editHeadOfficeView, name='edit_head_office'),
    path('delete_head_office/<int:head_office_id>/', views.delete_head_office, name='delete_head_office'),
    path('edit_branch/<int:branch_id>/', views.edit_branch, name='edit_branch'),
    path('delete_branch/<int:branch_id>/', views.delete_branch, name='delete_branch'),
    path('create-department/', views.create_department, name='create_department'),
    path('department_list/', views.departmentList, name='department_list'),
    path('edit_department/<int:department_id>/', views.edit_department, name='edit_department'),
    path('delete_department/<int:department_id>/', views.delete_department, name='delete_department'),
    path('department/<int:department_id>/', views.department_detail, name='department_detail'),
    path('department/assets/<int:department_id>/', views.department_assets, name='department_assets'),
    
    path('members/', views.commission_members_list, name='commission_members_list'),
    path('members/create/', views.commission_member_create, name='commission_member_create'),
    path('chairman/', views.chairman_list, name='chairman_list'),
    path('chairman/create/', views.chairman_create, name='chairman_create'),
    path('chairman/edit/<int:pk>/', views.chairman_edit, name='chairman_edit'),
    path('chairman/delete/<int:pk>/', views.chairman_delete, name='chairman_delete'),
    path('commission-member/edit/<int:pk>/', views.commission_member_edit, name='commission_member_edit'),
    path('commission-member/delete/<int:pk>/', views.commission_member_delete, name='commission_member_delete'),
    path('get-commission-members/', views.get_commission_members, name='get-commission-members'),
    
    
    path('change-language/<str:language_code>/', views.change_language, name='change_language'),
]
