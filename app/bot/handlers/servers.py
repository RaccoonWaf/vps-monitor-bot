import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from app.bot.messages import Messages
from app.bot.keyboards.inline import (
    protocols_keyboard,
    ports_keyboard,
    servers_list_keyboard,
    server_actions_keyboard,
)
from app.config import settings
from app.db.repositories.users import get_or_create_user
from app.db.repositories.servers import (
    add_server,
    get_user_servers,
    delete_server,
    count_user_servers,
)
from app.utils.ports import PROTOCOLS

router = Router()


class AddServer(StatesGroup):
    waiting_for_ip = State()
    waiting_for_protocol = State()
    waiting_for_port = State()


IP_REGEX = re.compile(
    r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$"
)


@router.message(Command("servers"))
@router.callback_query(F.data == "list_servers")
async def list_servers(event: Message | CallbackQuery):
    user = await get_or_create_user(event.from_user.id)
    servers = await get_user_servers(user["id"])

    text = Messages.NO_SERVERS if not servers else Messages.SERVER_LIST_HEADER
    markup = servers_list_keyboard(servers)

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=markup)
        await event.answer()
    else:
        await event.answer(text, reply_markup=markup)


@router.callback_query(F.data == "add_server")
@router.message(Command("add_server"))
async def start_add_server(event: Message | CallbackQuery, state: FSMContext):
    user = await get_or_create_user(event.from_user.id)
    count = await count_user_servers(user["id"])

    if count >= settings.max_servers_per_user:
        text = Messages.SERVER_LIMIT_REACHED.format(limit=settings.max_servers_per_user)
        if isinstance(event, CallbackQuery):
            await event.answer(text, show_alert=True)
        else:
            await event.answer(text)
        return

    await state.set_state(AddServer.waiting_for_ip)

    if isinstance(event, CallbackQuery):
        await event.message.answer(Messages.ADD_SERVER_IP)
        await event.answer()
    else:
        await event.answer(Messages.ADD_SERVER_IP)


@router.message(AddServer.waiting_for_ip)
async def process_ip(message: Message, state: FSMContext):
    ip = message.text.strip()

    if not IP_REGEX.match(ip):
        await message.answer(Messages.INVALID_IP)
        return

    await state.update_data(ip=ip)
    await state.set_state(AddServer.waiting_for_protocol)
    await message.answer(Messages.CHOOSE_PROTOCOL, reply_markup=protocols_keyboard())


@router.callback_query(AddServer.waiting_for_protocol, F.data.startswith("protocol:"))
async def process_protocol(callback: CallbackQuery, state: FSMContext):
    protocol_key = callback.data.split(":")[1]

    if protocol_key not in PROTOCOLS:
        await callback.answer("Неизвестный протокол", show_alert=True)
        return

    await state.update_data(protocol=protocol_key)
    await state.set_state(AddServer.waiting_for_port)

    await callback.message.edit_text(
        Messages.CHOOSE_PORT,
        reply_markup=ports_keyboard(protocol_key)
    )
    await callback.answer()


@router.callback_query(AddServer.waiting_for_port, F.data.startswith("port:"))
async def process_port(callback: CallbackQuery, state: FSMContext):
    port = int(callback.data.split(":")[1])
    data = await state.get_data()

    user = await get_or_create_user(callback.from_user.id)

    server = await add_server(
        user_id=user["id"],
        ip=data["ip"],
        port=port,
        protocol=data["protocol"]
    )

    protocol_name = PROTOCOLS[data["protocol"]]["name"]

    await callback.message.edit_text(
        Messages.SERVER_ADDED.format(
            ip=server["ip"],
            port=server["port"],
            protocol=protocol_name
        )
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("server:"))
async def server_detail(callback: CallbackQuery):
    server_id = int(callback.data.split(":")[1])
    await callback.message.edit_text(
        f"Сервер ID: {server_id}",
        reply_markup=server_actions_keyboard(server_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delete_server:"))
async def process_delete(callback: CallbackQuery):
    server_id = int(callback.data.split(":")[1])
    user = await get_or_create_user(callback.from_user.id)

    deleted = await delete_server(server_id, user["id"])

    if deleted:
        await callback.answer(Messages.SERVER_DELETED, show_alert=True)
    else:
        await callback.answer(Messages.SERVER_NOT_FOUND, show_alert=True)

    servers = await get_user_servers(user["id"])
    text = Messages.NO_SERVERS if not servers else Messages.SERVER_LIST_HEADER
    await callback.message.edit_text(
        text,
        reply_markup=servers_list_keyboard(servers)
        )


@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(Messages.CANCELLED)
    await callback.answer()
