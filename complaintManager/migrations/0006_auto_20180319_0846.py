# Generated by Django 2.0.3 on 2018-03-19 01:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('complaintManager', '0005_auto_20180318_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaintimages',
            name='log',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='complaintManager.Log'),
        ),
    ]
