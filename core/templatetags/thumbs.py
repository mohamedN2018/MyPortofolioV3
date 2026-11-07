"""
{{ image_field|thumb:800 }} → URL of a resized WebP copy (generated once, cached in MEDIA_ROOT/_thumbs/).

Large PNG screenshots (0.6–1.8 MB) made the gallery and project lists slow. Originals are never
modified; on any error the original URL is returned.
"""
import hashlib
import logging
from pathlib import Path

from django import template
from django.conf import settings

register = template.Library()
log = logging.getLogger(__name__)


@register.filter
def thumb(image, width=800):
    if not image:
        return ""
    try:
        src = Path(image.path)
        width = int(width)
        stat = src.stat()
        key = hashlib.sha1(f"{image.name}:{stat.st_size}:{int(stat.st_mtime)}:{width}".encode()).hexdigest()[:16]
        rel = f"_thumbs/{key}-{width}.webp"
        dest = Path(settings.MEDIA_ROOT) / rel
        if not dest.exists():
            from PIL import Image
            dest.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(src) as im:
                im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
                if im.width > width:
                    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
                tmp = dest.with_suffix(".tmp")
                im.save(tmp, "WEBP", quality=80, method=4)
                tmp.replace(dest)
        return settings.MEDIA_URL + rel
    except Exception as exc:  # missing file, unsupported format, read-only FS…
        log.warning("thumb failed for %s: %s", getattr(image, "name", image), exc)
        try:
            return image.url
        except Exception:
            return ""
