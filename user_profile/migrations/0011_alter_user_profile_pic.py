# Generated by Django 4.2.6 on 2023-10-28 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0010_alter_user_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_pic',
            field=models.ImageField(blank=True, default='/static/userprofile/default.png', null=True, upload_to='profile_pics/'),
        ),
    ]
