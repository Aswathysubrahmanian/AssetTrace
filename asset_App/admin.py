from django.contrib import admin

# Register your models here.
from .models import AssetData,AssetType,Asset_movement_data,Depreciation,CustomField,AssetImage,AssetBill



admin.site.register(AssetType)

admin.site.register(AssetData)
class AssetMovementDataAdmin(admin.ModelAdmin):
    list_display = ('asset', 'status', 'from_branch', 'to_branch', 'movement_date', 'return_date')
    list_filter = ('status', 'from_branch', 'to_branch', 'movement_date')
    search_fields = ('asset__asset_name', 'from_branch__branch_name', 'to_branch__branch_name')
    date_hierarchy = 'movement_date'

admin.site.register(Asset_movement_data, AssetMovementDataAdmin)
admin.site.register(Depreciation)
admin.site.register(CustomField)
admin.site.register(AssetImage)
admin.site.register(AssetBill)