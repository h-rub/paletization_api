from django.utils import timezone
from django.db import models

# Create your models here.
class Pallet(models.Model):
    identifier = models.CharField(max_length=200, unique=True)
    quantity = models.IntegerField(default=32)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_closed = models.DateTimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)

    def close_pallet(self):
        self.is_closed = True
        self.datetime_closed = timezone.now()
        self.save()

    def open_pallet(self):
        self.is_closed = False
        self.datetime_closed = None
        self.save()

    def __str__(self):
        return f"{self.identifier} - {self.quantity}"

class Component(models.Model):
    pallet = models.ForeignKey(Pallet, on_delete=models.CASCADE)
    condenser_unit_serial = models.CharField(max_length=250)
    condenser_material_code = models.CharField(max_length=250)
    compressor_unit_serial = models.CharField(max_length=250)
    compressor_material_code = models.CharField(max_length=250)
    material_type = models.CharField(max_length=10, null=True, blank=True)
    send_to_sap = models.BooleanField(default=False)
    sap_status = models.CharField(max_length=250, null=True, blank=True)
    serie = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return f"{self.code}"