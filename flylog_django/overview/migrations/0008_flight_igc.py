# Generated by Django 2.1.5 on 2020-05-30 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('overview', '0007_auto_20200530_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='igc',
            field=models.CharField(blank=True, default='', max_length=256, verbose_name='Trace IGC'),
        ),
    ]