# Generated by Django 4.2.7 on 2024-05-13 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppConstruction', '0002_admin'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeTravaux',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designation', models.CharField(max_length=200)),
                ('unite', models.CharField(max_length=5)),
                ('prix_unitaire', models.FloatField()),
            ],
        ),
    ]
