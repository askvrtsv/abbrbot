import logging
import os
import pathlib
import random

import telegram
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.environ["TELEGRAM_TOKEN"]
TEMPLATES_DIR = pathlib.Path(__file__).resolve().parent / "templates"


def setup_logging():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def load_template(template_path: pathlib.Path) -> str:
    return template_path.open(mode="r", encoding="utf-8").read()


def generate_abbr(length: int) -> str:
    SYMBOLS = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ"
    return "".join(random.choice(SYMBOLS) for _ in range(length))


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat

    await context.bot.send_message(
        update.effective_chat.id,
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
        text=load_template(TEMPLATES_DIR / "start.md"),
    )


async def handle_callback_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    assert update.callback_query

    query = update.callback_query
    await query.answer()

    match query.data:
        case None:
            pass
        case s if s.startswith("abbr-length"):
            length = int(s.split(":")[-1])
            await query.edit_message_text(generate_abbr(length))


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat
    assert update.message

    keyboard = [[
        telegram.InlineKeyboardButton("3", callback_data="abbr-length:3"),
        telegram.InlineKeyboardButton("4", callback_data="abbr-length:4"),
        telegram.InlineKeyboardButton("5", callback_data="abbr-length:5"),
    ]]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите размер:",
        reply_markup=reply_markup,
    )


def run_app():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler(["start", "help"], start_command))
    app.add_handler(CommandHandler("new", new_command))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.run_polling()


if __name__ == "__main__":
    setup_logging()
    run_app()
