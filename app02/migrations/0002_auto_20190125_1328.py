# Generated by Django 2.1.5 on 2019-01-25 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app02', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(max_length=150, verbose_name='标题'),
        ),
    ]