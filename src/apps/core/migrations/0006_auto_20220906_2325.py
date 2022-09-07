# Generated by Django 3.2.13 on 2022-09-06 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_blockednumber_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='external_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='external_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
