# Generated by Django 5.0.6 on 2024-07-10 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_alter_attendance_ip'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='random_code',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
