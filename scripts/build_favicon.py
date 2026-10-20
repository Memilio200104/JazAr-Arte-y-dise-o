"""Convert the supplied logo to browser icon formats without redrawing it."""
import sys
from pathlib import Path
from PIL import Image, ImageOps

source = Image.open(sys.argv[1]).convert('RGBA')
out = Path('static/icons')
out.mkdir(exist_ok=True)
for size, name in [(192, 'favicon-192.png'), (180, 'apple-touch-icon.png'), (256, 'favicon.ico')]:
    image = Image.new('RGBA', (size, size), 'white')
    logo = ImageOps.contain(source, (size, size), Image.Resampling.LANCZOS)
    image.alpha_composite(logo, ((size-logo.width)//2, (size-logo.height)//2))
    if name.endswith('.ico'):
        image.save(out/name, sizes=[(16,16),(32,32),(48,48),(64,64)])
    else:
        image.save(out/name)
