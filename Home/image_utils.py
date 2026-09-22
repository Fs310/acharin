from io import BytesIO
from pathlib import Path

from PIL import Image, ImageFilter, ImageStat
from django.core.files.base import ContentFile


def _smart_crop_16x9(image):
    target_ratio = 16 / 9
    width, height = image.size
    current_ratio = width / height

    if abs(current_ratio - target_ratio) < 0.01:
        return image

    if current_ratio > target_ratio:
        crop_width = int(height * target_ratio)
        max_left = width - crop_width

        # Evaluate several horizontal crops. Detail/edge density helps keep
        # the important subject instead of always taking the exact center.
        small = image.resize((min(320, width), max(1, int(min(320, width) * height / width))))
        edge = small.filter(ImageFilter.FIND_EDGES)
        scores = []
        for i in range(17):
            left = int(max_left * i / 16)
            box = (
                int(left * small.width / width),
                0,
                int((left + crop_width) * small.width / width),
                small.height,
            )
            candidate = edge.crop(box)
            score = ImageStat.Stat(candidate).mean[0]
            center_penalty = abs((left + crop_width / 2) - width / 2) / width
            scores.append((score - center_penalty * 4, left))

        left = max(scores)[1]
        return image.crop((left, 0, left + crop_width, height))

    crop_height = int(width / target_ratio)
    max_top = height - crop_height

    small_width = min(320, width)
    small = image.resize((small_width, max(1, int(small_width * height / width))))
    edge = small.filter(ImageFilter.FIND_EDGES)
    scores = []
    for i in range(17):
        top = int(max_top * i / 16)
        top_small = int(top * small.height / height)
        bottom_small = int((top + crop_height) * small.height / height)
        candidate = edge.crop((0, top_small, small.width, bottom_small))
        score = ImageStat.Stat(candidate).mean[0]
        center_penalty = abs((top + crop_height / 2) - height / 2) / height
        scores.append((score - center_penalty * 4, top))

    top = max(scores)[1]
    return image.crop((0, top, width, top + crop_height))


def build_16x9_thumbnail(instance):
    if not instance.sub_img or not instance.sub_img.name:
        return None

    if instance.sub_img.name.startswith(('http://', 'https://')):
        return None

    try:
        instance.sub_img.open('rb')
        image = Image.open(instance.sub_img).convert('RGB')
        image = _smart_crop_16x9(image)
        image.thumbnail((1200, 675), Image.Resampling.LANCZOS)

        output = BytesIO()
        image.save(output, format='JPEG', quality=88, optimize=True)
        name = f'{Path(instance.sub_img.name).stem}_16x9.jpg'
        return name, ContentFile(output.getvalue())
    except (OSError, ValueError, TypeError):
        return None
