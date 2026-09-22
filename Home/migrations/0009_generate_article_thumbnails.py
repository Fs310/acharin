from django.db import migrations


def generate_thumbnails(apps, schema_editor):
    from Home.image_utils import build_16x9_thumbnail

    SubNews = apps.get_model('Home', 'Sub_news')

    for article in SubNews.objects.exclude(sub_img='').exclude(sub_img__isnull=True).iterator():
        result = build_16x9_thumbnail(article)
        if not result:
            continue

        name, content = result
        article.sub_img_thumb.save(name, content, save=False)
        SubNews.objects.filter(pk=article.pk).update(
            sub_img_thumb=article.sub_img_thumb.name
        )


def reverse_thumbnails(apps, schema_editor):
    SubNews = apps.get_model('Home', 'Sub_news')
    for article in SubNews.objects.exclude(sub_img_thumb='').exclude(sub_img_thumb__isnull=True):
        if article.sub_img_thumb:
            article.sub_img_thumb.delete(save=False)
        SubNews.objects.filter(pk=article.pk).update(sub_img_thumb=None)


class Migration(migrations.Migration):
    dependencies = [
        ('Home', '0008_sub_news_sub_img_thumb'),
    ]

    operations = [
        migrations.RunPython(generate_thumbnails, reverse_thumbnails),
    ]
