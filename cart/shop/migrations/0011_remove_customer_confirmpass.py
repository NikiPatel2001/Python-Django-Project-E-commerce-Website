# Generated by Django 3.0.8 on 2021-03-04 04:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_customer_confirmpass'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='confirmpass',
        ),
    ]
