from django.db import models

# Create your models here.
class Component(models.Model):
    order = models.CharField(max_length=40, blank=True, null=True)
    condenser_unit_serial = models.CharField(max_length=250, unique=True)
    condenser_material_code = models.CharField(max_length=250, null=True, blank=True)
    condenser_status_test = models.BooleanField(default=False, null=True, blank=True)
    compressor_unit_serial = models.CharField(max_length=250, unique=True)
    compressor_material_code = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return f"{self.condenser_unit_serial} - {self.compressor_unit_serial}"