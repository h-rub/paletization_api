from django.contrib import admin
from .models import Component

@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ['condenser_unit_serial', 'condenser_material_code', 'condenser_status_test',
                    'compressor_unit_serial', 'compressor_material_code']
    list_filter = ['condenser_status_test', ]
    search_fields = ['condenser_unit_serial', 'compressor_unit_serial']

