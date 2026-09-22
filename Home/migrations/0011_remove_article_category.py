from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('Home', '0010_generate_article_thumbnails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sub_news',
            name='new',
        ),
        migrations.DeleteModel(
            name='News',
        ),
        migrations.AlterModelOptions(
            name='sub_news',
            options={
                'verbose_name': 'مقاله',
                'verbose_name_plural': 'مقالات',
            },
        ),
    ]
