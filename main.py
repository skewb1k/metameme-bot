import asyncio
from imaplib import Commands
import logging
import io
from operator import iadd
from re import T
import sys
from random import random
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    BufferedInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from forms import ImageForm
from image import ImageWrapper, open_image
from image_fetcher import get_from_bing
from phrase_generator import PhraseGenerator

TOKEN = getenv("BOT_TOKEN")

path_to_all_words = "data/all_words.txt"
BOTH_SIDES_CHANCE = 0.2
RANDOM_LETTERS_CHANCE = 0.1
RANDOM_DIGITS_CHANCE = 0.1
SINGLE_WORD_CHANCE = 0.5
CAPS_CHANCE = 0.5
MIN_RANDOM_LETTERS_LEN = 4
MAX_RANDOM_LETTERS_LEN = 7
MIN_WORDS_COUHT = 1
MAX_WORDS_COUNT = 3

GET_METAMEME_BUTTON = "Get metameme"
EDIT_IMAGE_BUTTON = "Edit your image"

SHAKALIZE_CALLBACK = "shakalize"
ADD_TEXT_CALLBACK = "add_text"
ADD_TEXT_AND_SHAKALIZE_CALLBACK = "add_text_and_shakalize"

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

default_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=GET_METAMEME_BUTTON),
            KeyboardButton(text=EDIT_IMAGE_BUTTON),
        ]
    ],
    resize_keyboard=True,
)

phrase_generator = PhraseGenerator(
    path_to_all_words,
    RANDOM_LETTERS_CHANCE,
    RANDOM_DIGITS_CHANCE,
    SINGLE_WORD_CHANCE,
    CAPS_CHANCE,
    MIN_RANDOM_LETTERS_LEN,
    MAX_RANDOM_LETTERS_LEN,
    MIN_WORDS_COUHT,
    MAX_WORDS_COUNT,
)


# todo: refactor all this shit.
def get_image_by_query(query: str) -> ImageWrapper:
    res = get_from_bing(query)
    if res:
        return ImageWrapper(open_image(io.BytesIO(res)))

    return None


async def answer_with_image(message: Message, image: ImageWrapper) -> None:
    await message.answer_photo(
        BufferedInputFile(
            file=image.get_img_byte_arr(),
            filename="file.png",
        )
    )


async def get_image_from_user(state):
    data = await state.get_data()

    file_in_io = io.BytesIO()
    await bot.download(
        file=data.get("image"),
        destination=file_in_io,
    )

    return ImageWrapper(open_image(file_in_io))


@dp.message(F.text == GET_METAMEME_BUTTON)
async def get_metameme_handler(message: Message):
    while 1:
        image = get_image_by_query(
            phrase_generator.get_random_phrase(
                size=2,
                allow_caps=False,
                allow_digits=False,
                allow_random_letters=False,
            )
        )
        if image:
            break

    image.low_quality_shortcut(3)
    if random() <= BOTH_SIDES_CHANCE:
        image.add_text(phrase_generator.get_random_phrase(), is_text_on_top=True)
        image.add_text(phrase_generator.get_random_phrase(), is_text_on_top=False)
    else:
        if random() <= 0.5:
            image.add_text(phrase_generator.get_random_phrase(), is_text_on_top=True)
        else:
            image.add_text(phrase_generator.get_random_phrase(), is_text_on_top=False)

    image.lower_quality(2)
    image.quantize(50)
    await answer_with_image(message, image)


@dp.message(F.text == EDIT_IMAGE_BUTTON)
async def shakalize_image_handler(message: Message, state: FSMContext):
    await state.set_state(ImageForm.image)
    await message.answer("Send me an image")


@dp.message(F.photo or ImageForm.image)
async def process_image(message: Message, state: FSMContext) -> None:
    await state.update_data(image=message.photo[-1].file_id)
    await state.set_state(ImageForm.command)
    await message.answer(
        f"Choose a command:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Add text and shakalize (Default)",
                        callback_data=ADD_TEXT_AND_SHAKALIZE_CALLBACK,
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Shakalize",
                        callback_data=SHAKALIZE_CALLBACK,
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Add text",
                        callback_data=ADD_TEXT_CALLBACK,
                    )
                ],
            ]
        ),
    )


async def request_for_text(state: FSMContext, callback_query: CallbackQuery) -> None:
    await state.set_state(ImageForm.waiting_for_text)
    await callback_query.answer(
        "Send me a text to add to the image. Devide top and bottom with a new line. For only bottom line leave - symbol on top line"
    )


@dp.callback_query(F.data == ADD_TEXT_AND_SHAKALIZE_CALLBACK)
async def add_text_and_shakalize_handler(
    callback_query: CallbackQuery, state: FSMContext
) -> None:
    await state.update_data(shakalize=True)
    await request_for_text(state, callback_query)


@dp.callback_query(F.data == SHAKALIZE_CALLBACK)
async def shakalize_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    image = await get_image_from_user(state)

    image.low_quality_shortcut(4)
    await answer_with_image(callback_query.message, image)

    await callback_query.answer()


@dp.callback_query(F.data == ADD_TEXT_CALLBACK)
async def add_text_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await request_for_text(state, callback_query)


@dp.message(ImageForm.waiting_for_text)
async def add_text_handler(message: Message, state: FSMContext) -> None:
    image = await get_image_from_user(state)
    text = message.text.split("\n")

    data = await state.get_data()
    if data.get("shakalize"):
        image.low_quality_shortcut(4)

    if text[0] != "-":
        image.add_text(text[0], is_text_on_top=True)
    if len(text) >= 2:
        image.add_text(text[1], is_text_on_top=False)

    if data.get("shakalize"):
        # image.lower_quality(2)
        image.quantize(50)

    await answer_with_image(message, image)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Choose an option:", reply_markup=default_keyboard)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
