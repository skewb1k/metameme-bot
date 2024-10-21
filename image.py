from PIL.ImageFile import ImageFile


class Image:
    def __init__(self, image: ImageFile):
        self.image = image

    def lower_image_quality(self, level: int) -> None:
        img_buffer = self.image.resize(
            (self.image.size[0] // level, self.image.size[1] // level), resample=None
        )
        img_buffer = img_buffer.resize(
            (self.image.size[0] * level, self.image.size[1] * level),
            resample=Image.Resampling.BOX,
        )

        self.image = img_buffer

    def change_contrast(self, level: int) -> None:
        factor = (259 * (level + 255)) / (255 * (259 - level))

        self.img.point(lambda x: 128 + factor * (x - 128))
