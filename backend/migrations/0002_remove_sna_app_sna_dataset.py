# Generated by Django 4.2.2 on 2024-02-09 20:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sna',
            name='app',
        ),
        migrations.AddField(
            model_name='sna',
            name='dataset',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='backend.dataset'),
        ),
    ]
