from io import BytesIO
from pathlib import Path

from PIL import Image
from django.core.files.base import ContentFile


def build_16x9_thumbnail(instance):
    if not instance.sub_img or not instance.sub_img.name:
        return None

    if instance.sub_img.name.startswith(('http://', 'https://')):
        return None

    try:
        instance.sub_img.open('rb')
        image = Image.open(instance.sub_img).convert('RGB')
        width, height = image.size
        target_ratio = 16 / 9
        current_ratio = width / height

        if current_ratio > target_ratio:
            crop_width = int(height * target_ratio)
            left = (width - crop_width) // 2
            image = image.crop((left, 0, left + crop_width, height))
        elif current_ratio < target_ratio:
            crop_height = int(width / target_ratio)
            top = (height - crop_height) // 2
            image = image.crop((0, top, width, top + crop_height))

        image.thumbnail((1200, 675), Image.Resampling.LANCZOS)
        output = BytesIO()
        image.save(output, format='JPEG', quality=88, optimize=True)
        name = f'{Path(instance.sub_img.name).stem}_16x9.jpg'
        return name, ContentFile(output.getvalue())
    except (OSError, ValueError, TypeError):
        return None
