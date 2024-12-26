from django.urls import path
from . import views

urlpatterns = [

    path('', views.asset_list, name='asset_list'),
    path('create/', views.asset_create, name='asset_create'),
    path('<int:pk>/',views. asset_detail, name='asset_detail'),
    path('<int:pk>/edit/', views.asset_edit, name='asset_edit'),
    path('<int:pk>/delete/', views.asset_delete, name='asset_delete'),
    path('asset/<int:asset_id>/', views.asset_link, name='asset_link'),
    path('download_qr_code/<int:asset_id>/', views.download_qr_code, name='download_qr_code'),
    path('asset-type-edit/<int:pk>/',views.asset_type_edit,name='type-edit'),
    path('asset-type-delete/<int:pk>/',views.asset_type_delete,name='asset-type-delete'),
    path('asset-type-create/',views.create_asset_type,name='asset_type'),
    path('verify-asset/<int:asset_id>/', views.verify_asset, name='verify_asset'),
    # path('upload-excel/', views.upload_excel, name='upload_excel'),
    path('delete-image/<int:image_id>/', views.delete_image, name='delete_image'),
    
    
    path('sold-assets/', views.sold_asset_list, name='sold_asset_list'),
    path('sold-assets/unsold/<int:asset_id>/', views.mark_as_unsold, name='mark_as_unsold'),
    path('sell/<int:pk>/', views.sell_asset, name='sell_asset'),
    #--------------------------------------------------------------------------------------------------
    path('asset-movement/list/', views.asset_movement_page, name='asset_movement_list'),
    path('assets/<int:branch_id>/', views.asset_filter_by_branches, name='asset_filter_by_branches'),
    path('asset-movements/edit/<int:movement_id>/', views.edit_asset_movement, name='edit_asset_movement'),
    path('get-branches/', views.get_branches, name='get_branches'),   
    path('get-asset-branch/', views.get_asset_branch, name='get_asset_branch'),
    path('get-custom-fields/', views.get_custom_fields, name='get_custom_fields'),
    
    
    
    path('api/branch-prefix/<int:branch_id>/', views.get_branch_prefix, name='branch_prefix'),
    path('api/generate-asset-code/<int:branch_id>/', views.generate_asset_code, name='generate_asset_code'),
    #-----------------------------------------------------------------------------------------------------
 
 
    path('depreciation/create/', views.create_depreciation, name='create_depreciation'),
    path('depreciation/create/custom/', views.create_custom_depreciation, name='create_custom_depreciation'),
    path('depreciation/<int:pk>/', views.depreciation_detail, name='depreciation_detail'),
    path('assets/depreciation/', views.asset_depreciation_list, name='asset_depreciation_list'),
    path('depreciation/<int:pk>/delete/', views.delete_depreciation, name='delete_depreciation'),
    path('depreciation/standard/<int:pk>/edit/', views.edit_standard_depreciation, name='edit_standard_depreciation'),
    path('depreciation/custom/<int:pk>/edit/', views.edit_custom_depreciation, name='edit_custom_depreciation'),
    
    #------------------------------------------------------------------------------------------------------
    
    
    path('export-excel/', views.export_excel, name='export_excel'),
    path('export-pdf/', views.export_pdf, name='export_pdf'),
    path('Asset-report/', views.asset_report_view, name='reports'),
    # path('export-asset-report/', views.export_asset_report, name='export_asset_report'),
    path('reports/chart-data/', views.get_chart_data, name='chart_data'),
    path('reports/export-pdf/', views.export_pdf, name='export_pdf'),
    path('upload-assets/', views.upload_assets, name='upload_assets'),
    path('download-template/',views.download_template,name='download_template'),
    path('export-report/', views.export_report, name='export_report'),
    path('export-excel-report/', views.export_excel_report, name='export_excel_report'),
    path('export-pdf-report/', views.export_pdf_report, name='export_pdf_report'),
    

]