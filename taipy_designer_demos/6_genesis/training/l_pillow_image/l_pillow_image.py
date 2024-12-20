from taipy.gui import Gui
from taipy.designer import Page

from pathlib import Path
from PIL import Image, ImageOps


def convert_to_grayscale(image, intensity):
    """Convert an image to grayscale with a given intensity."""
    if intensity < 0:
        intensity = 0
    if intensity > 1:
        intensity = 1
    img_grey = ImageOps.grayscale(image).point(
        lambda x: x * intensity + 255 * (1 - intensity)
    )
    return img_grey


image_path = Path(__file__).parent.resolve() / "XN_Fruehjahrswiese_00.jpg"

image = Image.open(image_path)

img_grey = convert_to_grayscale(image, 1)

greyscale_intensity = 1


def on_change(state, var, val):
    if var == "greyscale_intensity":
        state.img_grey = convert_to_grayscale(state.image, val)


page = Page("l_pillow_image.xprjson")
Gui(page).run(design=True)
