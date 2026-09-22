from django.db.models.signals import post_save
from django.dispatch import receiver

from .image_utils import build_16x9_thumbnail
from .models import Sub_news


@receiver(post_save, sender=Sub_news)
def generate_article_thumbnail(sender, instance, **kwargs):
    if not instance.sub_img:
        return

    source_name = instance.sub_img.name
    existing_name = instance.sub_img_thumb.name if instance.sub_img_thumb else ''
    expected_name = f'{source_name.rsplit("/", 1)[-1].rsplit(".", 1)[0]}_16x9.jpg'

    if existing_name and existing_name.endswith(expected_name):
        return

    result = build_16x9_thumbnail(instance)
    if not result:
        return

    name, content = result
    instance.sub_img_thumb.save(name, content, save=False)
    sender.objects.filter(pk=instance.pk).update(sub_img_thumb=instance.sub_img_thumb.name)
