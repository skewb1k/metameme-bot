import asyncio
import logging
import sys
import io
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, BufferedInputFile

from image_editor import (
    change_contrast,
    add_random_text,
    open_image,
)
from image_fetcher import fetch_image_by_query
from phrase_generator import get_random_phrase

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message) -> None:
    while 1:
        resp = fetch_image_by_query(
            get_random_phrase(
                size=2,
                allow_caps=False,
                allow_digits=False,
                allow_random_letters=False,
            )
        )
        if resp:
            break

    image = open_image(resp)
    image = add_random_text(change_contrast(image.quantize(50, method=1), 0.05))
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()

    input_file = BufferedInputFile(
        file=img_byte_arr,
        filename="file.jpg",
    )

    await message.answer_photo(input_file)


async def main() -> None:
    if TOKEN is None:
        raise RuntimeError("No token provided")

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
