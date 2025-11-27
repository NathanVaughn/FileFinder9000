import os

from PIL import Image

png_image = Image.open(os.path.join("images", "icon_256.png"))
png_image.save(os.path.join("images", "icon.ico"))
png_image.save(os.path.join("images", "icon.icns"))

png_image_no_alpha = png_image.convert("1")
png_image_no_alpha.save(os.path.join("images", "icon.xbm"))