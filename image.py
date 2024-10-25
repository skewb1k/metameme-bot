import io
from operator import le
from PIL.ImageFile import ImageFile
from PIL import Image, ImageFont, ImageDraw, ImageEnhance


def open_image(res):
    return Image.open(res)


class ImageWrapper:

    def __init__(self, image: ImageFile):
        self.image = image.convert("RGB")
        self.font_name = "fonts/impact.ttf"

    def lower_quality(self, level: int) -> None:
        img_buffer = self.image.resize(
            (self.image.size[0] // level, self.image.size[1] // level),
            resample=Image.Resampling.NEAREST,
        )
        img_buffer = img_buffer.resize(
            (img_buffer.size[0] * 3 * level, img_buffer.size[1] * 3 * level),
            resample=Image.Resampling.NEAREST,
        )

        self.image = img_buffer

    def change_contrast(self, level: int) -> None:
        img = self.image.convert("RGB")
        self.image = ImageEnhance.Contrast(img).enhance(level)

    def change_brightness(self, level: int) -> None:
        img = self.image.convert("RGB")
        self.image = ImageEnhance.Brightness(img).enhance(level)

    def add_text(self, text: str, is_text_on_top: bool) -> ImageFile:
        draw = ImageDraw.Draw(self.image)

        width, height = self.image.size
        fontsize = 1  # starting font size
        max_width = 0.85
        x = width // 2

        while 1:
            fontsize += 1
            font = ImageFont.truetype(self.font_name, fontsize)
            if (
                (font.getbbox(text)[2] - font.getbbox(text)[0]) > max_width * width
            ) or (font.getbbox(text)[3] - font.getbbox(text)[1] > 0.15 * height):
                break

        if is_text_on_top:
            y = (height * 0.03) + ((font.getbbox(text)[3] - font.getbbox(text)[1]) // 2)
        else:
            y = (height * 0.97) - ((font.getbbox(text)[3] - font.getbbox(text)[1]) // 2)

        offset = fontsize // 14
        draw.text((x - offset, y), text, font=font, anchor="mm", fill="black")
        draw.text((x + offset, y), text, font=font, anchor="mm", fill="black")
        draw.text((x, y + offset), text, font=font, anchor="mm", fill="black")
        draw.text((x, y - offset), text, font=font, anchor="mm", fill="black")
        draw.text((x - offset, y + offset), text, font=font, anchor="mm", fill="black")
        draw.text((x + offset, y + offset), text, font=font, anchor="mm", fill="black")
        draw.text((x - offset, y - offset), text, font=font, anchor="mm", fill="black")
        draw.text((x + offset, y - offset), text, font=font, anchor="mm", fill="black")

        draw.text((x, y), text, font=font, anchor="mm", fill="#fff")
        del draw

        return self.image

    def quantize(self, level: int) -> None:
        self.image = self.image.quantize(level, method=1)

    def low_quality_shortcut(self, level: int) -> ImageFile:
        match level:
            case 1:
                self.lower_quality(2)
                self.quantize(50)
            case 2:
                self.lower_quality(2)
                self.quantize(50)
            case 3:
                self.change_contrast(1.1)
                self.lower_quality(2)
                self.quantize(30)
            case 4:
                self.change_contrast(1.3)
                self.lower_quality(4)
                self.quantize(30)
            case 5:
                self.change_contrast(1.3)
                self.change_brightness(1.1)
                self.lower_quality(8)
                self.quantize(30)

        return self.image

    def get_img_byte_arr(self) -> bytes:
        img_byte_arr = io.BytesIO()

        self.image.save(img_byte_arr, format="PNG", optimization=True, quality=10)
        img_byte_arr = img_byte_arr.getvalue()

        return img_byte_arr
