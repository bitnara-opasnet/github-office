# Generated by Django 3.2.7 on 2021-10-05 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('title', models.TextField()),
                ('contents', models.TextField()),
                ('create_date', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
