# Generated by Django 5.0.2 on 2024-03-04 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SmartUsers', '0002_category_subcategory_course_video'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutorprofile',
            name='is_approved',
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_approved',
            field=models.BooleanField(default=True),
        ),
    ]
