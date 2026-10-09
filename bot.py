import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

import database as db

BOT_TOKEN = "8816025163:AAFsRWko7dviV80HlZ7tk9AxU0MkqbI_iic"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()


class AddProductFSM(StatesGroup):
    waiting_for_drink_1 = State()
    waiting_for_drink_2 = State()
    waiting_for_drink_3 = State()


main_buttons = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="/menu")]], resize_keyboard=True
)

about_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="О нас", callback_data="about")]
    ]
)


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    text = (
        " <b>Список команд:</b>\n\n"
        "/menu — Список всех команд\n"
        "/drinks — Посмотреть список напитков\n"
        "/add_product — Добавить 3 напитка в меню\n"
        "/about — Информация о кафе"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=main_buttons)

@router.message(F.text.lower() == "пока")
async def handle_bye(message: Message):
    await message.answer("До встречи!")


@router.message(Command("about"))
async def cmd_about(message: Message):
    await message.answer(
        "Нажмите кнопку ниже, чтобы узнать о нас:", reply_markup=about_inline_kb
    )


@router.callback_query(F.data == "about")
async def process_about_callback(callback: CallbackQuery):
    await callback.message.answer(
        " Мы - уютное кафе, где готовят самый вкусный кофе в городе!"
    )
    await callback.answer()

@router.message(Command("add_product"))
async def start_add_product(message: Message, state: FSMContext):
    await state.set_state(AddProductFSM.waiting_for_drink_1)
    await message.answer("Введите название первого напитка:")


@router.message(AddProductFSM.waiting_for_drink_1)
async def process_drink_1(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Пожалуйста, введите название текстом, а не картинкой или стикером!"
        )
        return

    await db.add_product(message.text.strip())
    await state.set_state(AddProductFSM.waiting_for_drink_2)
    await message.answer("Отлично! Введите название второго напитка:")


@router.message(AddProductFSM.waiting_for_drink_2)
async def process_drink_2(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Пожалуйста, введите название текстом, а не картинкой или стикером!"
        )
        return

    await db.add_product(message.text.strip())
    await state.set_state(AddProductFSM.waiting_for_drink_3)
    await message.answer("Супер! Введите название третьего напитка:")


@router.message(AddProductFSM.waiting_for_drink_3)
async def process_drink_3(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Пожалуйста, введите название текстом, а не картинкой или стикером!"
        )
        return

    await db.add_product(message.text.strip())
    await state.clear()
    await message.answer("Все 3 напитка успешно добавлены в меню! ")


@router.message(Command("drinks"))
async def cmd_drinks(message: Message):
    products = await db.get_all_products()
    if not products:
        await message.answer("Меню пока пустое")
    else:
        text = " **Список напитков:**\n\n" + "\n".join(
            [f"• {item}" for item in products]
        )
        await message.answer(text, parse_mode="Markdown")


async def main():
    logging.basicConfig(level=logging.INFO)
    await db.init_db()

    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)

    print("--- БОТ УСПЕШНО ЗАПУЩЕН И ГОТОВ К РАБОТЕ ---")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())