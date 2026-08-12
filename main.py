import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, URLInputFile

from groq import Groq

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher()

user_history = {}

logging.basicConfig(level=logging.INFO)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🖼 IT Live Rasmi"),
            KeyboardButton(text="ℹ️ Biz haqimizda")
        ],
        [
            KeyboardButton(text="📞 Aloqa va manzil")
        ]
    ],
    resize_keyboard=True
)


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_history[message.from_user.id] = []

    await message.answer(
        "Salom! Men Ai botman,sizga qadey yordam kerak? ",
        reply_markup=main_keyboard
    )


@dp.message(lambda msg: msg.text == "🖼 IT Live Rasmi")
async def send_it_live_photo(message: types.Message):
    photo_url = "https://dummyimage.com/800x500/000000/ffffff.png&text=IT+LIVE"
    photo = URLInputFile(photo_url, filename="it_live.png")

    await message.answer_photo(
        photo=photo,
        caption="🖼 **IT Live Academy**",
        reply_markup=main_keyboard
    )


@dp.message(lambda msg: msg.text == "ℹ️ Biz haqimizda")
async def about_us_handler(message: types.Message):
    await message.answer(
        'Salom bu bot sizni qiziqtirgan savolarga javob beradi.Bot ni "Oybekov Nurbek", yaratdi!',
        reply_markup=main_keyboard
    )


@dp.message(lambda msg: msg.text == "📞 Aloqa va manzil")
async def contact_handler(message: types.Message):
    await message.answer(
        "📞 **Telefon:** +998 90 123 45 67\n"
        "📍 **Manzil:** Guliston shaxar It live academy",
        reply_markup=main_keyboard
    )


@dp.message()
async def ai_chat_handler(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_history:
        user_history[user_id] = []

    user_history[user_id].append({"role": "user", "content": message.text})

    messages_to_send = [
                           {
                               "role": "system",
                               "content": "Siz Guliston shahridagi IT Live Academy o'quv markazining aqlli va tezkor sun'iy intellekt yordamchisiz."
                           }
                       ] + user_history[user_id][-6:]

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages_to_send,
            temperature=0.7,
            max_tokens=1000
        )

        ai_response = completion.choices[0].message.content
        user_history[user_id].append({"role": "assistant", "content": ai_response})

        await message.answer(ai_response, reply_markup=main_keyboard)

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.answer("⚠️ Xatolik yuz berdi. Qaytadan urinib ko'ring.", reply_markup=main_keyboard)


async def main():
    print("🚀 Bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
