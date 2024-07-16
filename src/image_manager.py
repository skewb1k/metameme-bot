from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import io
from phrase_generator import get_random_phrase
from random import random

BOTH_SIDES_CHANCE = 0.2


def change_quality(img, level):
    img = img.resize((img.size[0] // level, img.size[1] // level), resample=None)
    img = img.resize(
        (img.size[0] * level, img.size[1] * level), resample=Image.Resampling.BOX
    )

    return img


def change_contrast(img, level):
    factor = (259 * (level + 255)) / (255 * (259 - level))

    def contrast(c):
        return 128 + factor * (c - 128)

    return img.point(contrast)


def open_image(res):
    return Image.open(io.BytesIO(res))


def add_text(img, text, side):
    font_name = "fonts/impact.ttf"
    draw = ImageDraw.Draw(img)
    width, height = img.size
    fontsize = 1  # starting font size
    max_width = 0.9
    x = width // 2

    font = ImageFont.truetype(font_name, fontsize)
    while (font.getbbox(text)[2] - font.getbbox(text)[0]) < max_width * width:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype(font_name, fontsize)

    font = ImageFont.truetype(font_name, fontsize)
    if side == 'top':
        y = (height * 0.05) + ((font.getbbox(text)[3] - font.getbbox(text)[1]) // 2)
    else:
        y = (height * 0.95) - ((font.getbbox(text)[3] - font.getbbox(text)[1]) // 2)
    offset = 4

    for off in range(offset):
        draw.text((x - off, y), text, font=font, anchor="mm", fill='black')
        draw.text((x + off, y), text, font=font, anchor="mm", fill='black')
        draw.text((x, y + off), text, font=font, anchor="mm", fill='black')
        draw.text((x, y - off), text, font=font, anchor="mm", fill='black')
        draw.text((x - off, y + off), text, font=font, anchor="mm", fill='black')
        draw.text((x + off, y + off), text, font=font, anchor="mm", fill='black')
        draw.text((x - off, y - off), text, font=font, anchor="mm", fill='black')
        draw.text((x + off, y - off), text, font=font, anchor="mm", fill='black')

    draw.text((x, y), text, font=font, anchor="mm", fill="#fff")
    del draw
    return img


def shakal_image(img):
    enhancer = ImageEnhance.Brightness(img)
    i = enhancer.enhance(1.1)
    i = change_contrast(i, 5)
    # i = change_quality(i, 2).

    return i


def randomize_image(img):
    if random() <= BOTH_SIDES_CHANCE:
        return add_text(
            add_text(
                img,
                get_random_phrase(),
                'top',
            ),
            get_random_phrase(),
            'bot',
        )
    if random() <= 0.5:
        return add_text(
            img,
            get_random_phrase(),
            'top',
        )
    else:
        return add_text(
            img,
            get_random_phrase(),
            'bot',
        )
