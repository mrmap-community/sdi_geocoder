# Generated by Django 4.2.15 on 2024-09-02 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sdi_geocoder', '0006_geocoding_geocodingresult'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ogcapifeatures',
            name='name',
        ),
        migrations.AddField(
            model_name='ogcapifeatures',
            name='title',
            field=models.CharField(default='', max_length=1024, verbose_name='Titel'),
            preserve_default=False,
        ),
    ]
