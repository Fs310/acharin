from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('Home', '0007_seed_articles')]

    operations = [
        migrations.AddField(
            model_name='sub_news',
            name='sub_img_thumb',
            field=models.ImageField(blank=True, editable=False, null=True, upload_to='blog/thumbs', verbose_name='تصویر 16:9'),
        ),
    ]
