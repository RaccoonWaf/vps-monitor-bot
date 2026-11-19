from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from app.bot.messages import Messages
from app.db.repositories.users import get_or_create_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await get_or_create_user(telegram_id=message.from_user.id)

    await message.answer(
        Messages.START.format(name=message.from_user.first_name)
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(Messages.HELP)
