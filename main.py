import asyncio
import logging
import io
import sys
from random import random
from os import getenv

from aiogram import Bot, Dispatcher, F, Router
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
CHANNEL_ID = getenv("CHANNEL_ID")
METAMEME_INTERVAL = int(getenv("METAMEME_INTERVAL"))

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
GET_RANDOM_IMAGE_BUTTON = "Get random image"

SHAKALIZE_CALLBACK = "shakalize"
ULTRA_SHAKALIZE_CALLBACK = "ultra_shakalize"
ADD_TEXT_CALLBACK = "add_text"
ADD_TEXT_AND_SHAKALIZE_CALLBACK = "add_text_and_shakalize"

dp = Dispatcher()
router = Router()
dp.include_router(router)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

default_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=GET_METAMEME_BUTTON),
            KeyboardButton(text=EDIT_IMAGE_BUTTON),
            KeyboardButton(text=GET_RANDOM_IMAGE_BUTTON),
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


# todo: refactor all this stuff.
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


async def download_image(image: str):
    file_in_io = io.BytesIO()
    await bot.download(
        file=image,
        destination=file_in_io,
    )

    return ImageWrapper(open_image(file_in_io))


async def start_user_image(message: Message, state: FSMContext, image: str) -> None:
    await state.update_data(image=image)
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
                        text="Ultra skalize",
                        callback_data=ULTRA_SHAKALIZE_CALLBACK,
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


@router.message(F.text == GET_RANDOM_IMAGE_BUTTON)
async def get_random_image_handler(message: Message, state: FSMContext) -> None:
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

    await answer_with_image(message, image)
    await start_user_image(message, state=state, image=image)


def get_metameme() -> ImageWrapper:
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

    image.low_quality_shortcut(1)
    if random() <= BOTH_SIDES_CHANCE:
        image.add_text(phrase_generator.get_random_phrase(), is_text_on_top=True)
        image.add_text(phrase_generator.get_random_phrase(), is_text_on_top=False)
    else:
        if random() <= 0.5:
            image.add_text(phrase_generator.get_random_phrase(), is_text_on_top=True)
        else:
            image.add_text(phrase_generator.get_random_phrase(), is_text_on_top=False)

    image.quantize(50)

    return image


@router.message(F.text == GET_METAMEME_BUTTON)
async def get_metameme_handler(message: Message):
    image = get_metameme()
    await answer_with_image(message, image)


@router.message(F.text == EDIT_IMAGE_BUTTON)
async def shakalize_image_handler(message: Message, state: FSMContext):
    await state.set_state(ImageForm.image)
    await message.answer("Send me an image")


@router.message(F.photo or ImageForm.image)
async def user_image_handler(message: Message, state: FSMContext) -> None:
    image = await download_image(message.photo[-1].file_id)
    await start_user_image(message, state, image)


async def request_for_text(state: FSMContext, callback_query: CallbackQuery) -> None:
    await state.set_state(ImageForm.waiting_for_text)
    await callback_query.answer(
        "Send me a text to add to the image. Devide top and bottom with a new line. For only bottom line leave - symbol on top line"
    )


@router.callback_query(F.data == ADD_TEXT_AND_SHAKALIZE_CALLBACK)
async def add_text_and_shakalize_handler(
    callback_query: CallbackQuery, state: FSMContext
) -> None:
    await state.update_data(shakalize=True)
    await request_for_text(state, callback_query)


@router.callback_query(F.data == SHAKALIZE_CALLBACK)
async def shakalize_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    image = data.get("image")

    image.low_quality_shortcut(1)
    await answer_with_image(callback_query.message, image)

    await callback_query.answer()


@router.callback_query(F.data == ULTRA_SHAKALIZE_CALLBACK)
async def ultra_shakalize_handler(
    callback_query: CallbackQuery, state: FSMContext
) -> None:
    data = await state.get_data()
    image = data.get("image")

    image.low_quality_shortcut(4)
    await answer_with_image(callback_query.message, image)

    await callback_query.answer()


@router.callback_query(F.data == ADD_TEXT_CALLBACK)
async def add_text_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await request_for_text(state, callback_query)


@router.message(ImageForm.waiting_for_text)
async def add_text_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    image = data.get("image")

    text = message.text.split("\n")

    if data.get("shakalize"):
        image.low_quality_shortcut(1)

    if text[0] != "-":
        image.add_text(text[0], is_text_on_top=True)
    if len(text) >= 2:
        image.add_text(text[1], is_text_on_top=False)

    if data.get("shakalize"):
        image.quantize(50)

    await answer_with_image(message, image)
    await state.clear()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Choose an option:", reply_markup=default_keyboard)


async def send_metameme_to_channel() -> None:
    image = get_metameme()
    await bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=BufferedInputFile(
            file=image.get_img_byte_arr(),
            filename="file.png",
        ),
    )


async def spam_metamemes_in_channel(stop_event: asyncio.Event):
    while not stop_event.is_set():
        await send_metameme_to_channel()
        await asyncio.sleep(METAMEME_INTERVAL)


async def main(stop_event: asyncio.Event) -> None:
    try:
        await dp.start_polling(bot)
    finally:
        stop_event.set()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    stop_event = asyncio.Event()

    async def run_both():
        await asyncio.gather(spam_metamemes_in_channel(stop_event), main(stop_event))

    try:
        asyncio.run(run_both())
    except KeyboardInterrupt:
        logging.info("Bot stopped")
