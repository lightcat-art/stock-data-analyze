# Generated by Django 3.2.15 on 2022-09-24 16:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocksimul', '0006_rename_row_stockprice_low'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stockprice',
            old_name='end',
            new_name='close',
        ),
    ]
