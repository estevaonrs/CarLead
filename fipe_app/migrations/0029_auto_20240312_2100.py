# Generated by Django 3.2.13 on 2024-03-13 00:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fipe_app', '0028_lead_revisions_done_in_css_lead_under_warranty'),
    ]

    operations = [
        migrations.CreateModel(
            name='FipeVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='fipe_app.fipebrand')),
            ],
        ),
        migrations.AddField(
            model_name='fipemodel',
            name='version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fipe_app.fipeversion'),
        ),
    ]
