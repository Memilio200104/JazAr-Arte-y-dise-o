"""Extract PDF image objects for lossless source selection (requires pypdf/Pillow)."""
import sys
from pathlib import Path
from pypdf import PdfReader

reader = PdfReader(next(Path(sys.argv[1]).glob('*.pdf')))
destination = Path('artifacts/pdf-images')
destination.mkdir(exist_ok=True)
for page in [6, 11, 19, 20, 22, 24, 29, 31]:
    for index, image in enumerate(reader.pages[page - 1].images):
        image.image.save(destination / f'p{page:02d}-{index}.png')
