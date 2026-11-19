from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.utils.ports import PROTOCOLS


def protocols_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, data in PROTOCOLS.items():
        builder.button(
            text=data["name"],
            callback_data=f"protocol:{key}"
        )
    builder.button(text="Отмена", callback_data="cancel")
    builder.adjust(1)
    return builder.as_markup()


def ports_keyboard(protocol_key: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    ports = PROTOCOLS[protocol_key]["ports"]
    for port in ports:
        builder.button(
            text=str(port),
            callback_data=f"port:{port}"
        )
    builder.button(text="Отмена", callback_data="cancel")
    builder.adjust(3)
    return builder.as_markup()


def servers_list_keyboard(servers: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for server in servers:
        status = "🟢" if server["last_status"] is True else "🔴" if server["last_status"] is False else "⚪"
        text = f"{status} {server['ip']}:{server['port']}"
        builder.button(
            text=text,
            callback_data=f"server:{server['id']}"
        )
    builder.button(text="Добавить сервер", callback_data="add_server")
    builder.adjust(1)
    return builder.as_markup()


def server_actions_keyboard(server_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Удалить", callback_data=f"delete_server:{server_id}")
    builder.button(text="« Назад", callback_data="list_servers")
    builder.adjust(1)
    return builder.as_markup()
