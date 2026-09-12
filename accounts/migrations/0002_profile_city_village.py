from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='شهر'),
        ),
        migrations.AddField(
            model_name='profile',
            name='village',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='روستا'),
        ),
    ]
