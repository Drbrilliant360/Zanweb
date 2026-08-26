from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteerprofile',
            name='country',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='volunteerprofile',
            name='swahili_level',
            field=models.CharField(
                blank=True,
                choices=[('basic', 'Basic'), ('intermediate', 'Intermediate'), ('fluent', 'Fluent')],
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name='VolunteerExperience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('organization', models.CharField(blank=True, max_length=200)),
                ('dates', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('sort_order', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('volunteer', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='experiences',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['sort_order', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='VolunteerEducation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('degree', models.CharField(max_length=200)),
                ('school', models.CharField(blank=True, max_length=200)),
                ('dates', models.CharField(blank=True, max_length=100)),
                ('sort_order', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('volunteer', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='education_entries',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['sort_order', '-created_at'],
            },
        ),
    ]
