"""Rebuild the original geometric AudioDrop icon (requires Pillow)."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent / 'assets'
root.mkdir(exist_ok=True)
image = Image.new('RGBA', (256, 256))
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((8, 8, 248, 248), radius=54, fill='#101827')
draw.rounded_rectangle((44, 94, 64, 162), radius=10, fill='#47ddbb')
draw.rounded_rectangle((78, 66, 98, 190), radius=10, fill='#47ddbb')
draw.rounded_rectangle((112, 45, 132, 168), radius=10, fill='#47ddbb')
draw.polygon([(154, 95), (184, 95), (184, 151), (207, 151), (169, 197), (131, 151), (154, 151)], fill='#ffffff')
image.save(root / 'audiodrop.png')
image.save(root / 'audiodrop.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
