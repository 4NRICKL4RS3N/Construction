# Generated by Django 4.2.7 on 2024-05-13 18:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('AppConstruction', '0008_prixmaison'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetailDevis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designation', models.CharField(max_length=200, null=True)),
                ('unite', models.CharField(max_length=5, null=True)),
                ('prix_unitaire', models.FloatField(null=True)),
                ('prix_total', models.FloatField(null=True)),
                ('devis', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='AppConstruction.devis')),
                ('travaux', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='AppConstruction.travaux')),
            ],
        ),
    ]
