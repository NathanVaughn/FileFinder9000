import os

from PIL import Image

png_image = Image.open(os.path.join("images", "icon_256.png"))
png_image.save(os.path.join("images", "icon.ico"))
