# Generated by Django 4.2.6 on 2023-11-08 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pallets', '0004_remove_mountedcomponent_sap_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pallet',
            name='sap_success',
            field=models.BooleanField(default=False),
        ),
    ]