from fastapi import Depends, FastAPI, Form

from sqlalchemy.ext.asyncio import AsyncSession

from constants import UNRECOGNIZED_COMMAND_MESSAGE
from models import SessionLocal
from utils import determine_command, send_message_via_whatsapp
from webhooks import (
    find_or_create_user,
    handle_add_command,
    handle_delete_command,
    handle_show_command,
)

app = FastAPI()


async def get_db():
    """Асинхронный генератор для получения сессии базы данных."""
    async with SessionLocal() as session:
        yield session


@app.post("/webhooks/whatsapp/")
async def whatsapp_webhook(
    Body: str = Form(), From: str = Form(), db: AsyncSession = Depends(get_db)
):
    """Обработчик веб-хука для WhatsApp."""
    user, sent_welcome_message = await find_or_create_user(From, db)

    if sent_welcome_message:
        return {"success": True}

    command_type = determine_command(Body)

    if command_type == "show":
        response_message = await handle_show_command(user, db)
    elif command_type == "add":
        response_message = await handle_add_command(Body, user, db, From)
    elif command_type == "delete":
        response_message = await handle_delete_command(Body, user, db)
    else:
        response_message = UNRECOGNIZED_COMMAND_MESSAGE

    await send_message_via_whatsapp(response_message, to=From)
    return {"success": True}
