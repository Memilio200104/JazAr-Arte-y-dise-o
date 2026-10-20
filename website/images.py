from io import BytesIO
from uuid import uuid4
import warnings

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, ImageOps, UnidentifiedImageError


def prepare_image(upload):
    """Decode untrusted input and store only a bounded, metadata-free raster."""
    if upload.size > 5 * 1024 * 1024:
        raise ValidationError('La imagen no puede superar 5 MiB.')
    upload.seek(0)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(upload) as source:
                if source.format not in {'JPEG', 'PNG', 'WEBP'} or getattr(source, 'n_frames', 1) != 1:
                    raise ValidationError('Usa JPEG, PNG o WebP sin animacion.')
                if source.width * source.height > 20_000_000:
                    raise ValidationError('La imagen no puede superar 20 megapixeles.')
                source.load()
                alpha = 'A' in source.getbands() or 'transparency' in source.info
                image = ImageOps.exif_transpose(source).convert('RGBA' if alpha else 'RGB')
                image.thumbnail((2400, 2400))
                image.info.clear()
                output = BytesIO()
                image.save(output, format='WEBP', quality=85)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as exc:
        raise ValidationError('No se pudo leer la imagen. Usa un archivo valido.') from exc
    finally:
        upload.seek(0)
    return ContentFile(output.getvalue(), name=f'{uuid4().hex}.webp')


def validate_image(upload):
    prepare_image(upload)


def process_fields(instance, names):
    for name in names:
        field = getattr(instance, name)
        if field and not field._committed:
            setattr(instance, name, prepare_image(field))
