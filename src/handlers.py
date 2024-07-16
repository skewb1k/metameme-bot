import io
from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from image_manager import change_contrast, open_image, randomize_image
from phrase_generator import get_random_phrase
from image_fetcher import *

router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(
        "Привет! Я помогу тебе узнать твой ID, просто отправь мне любое сообщение"
    )


@router.message(Command("get_image"))
async def start_handler(msg: Message):
    while 1:
        image = fetch_image_by_query(
            get_random_phrase(
                size=2,
                allow_caps=False,
                allow_digits=False,
                allow_random_letters=False,
            )
        )
        if image:
            image = randomize_image(
                change_contrast(open_image(image).quantize(50, method=1), 0.05)
            )
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            input_file = BufferedInputFile(
                img_byte_arr,
                filename="file.jpg",
            )
            break

    await msg.answer_photo(input_file)
