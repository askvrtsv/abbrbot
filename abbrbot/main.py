import logging
import os
import pathlib
import random
import typing as t

import telegram
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

Lang = t.Literal["ru", "en"]

TOKEN = os.environ["TELEGRAM_TOKEN"]
TEMPLATES_DIR = pathlib.Path(__file__).resolve().parent / "templates"

LANGUAGES = {
    "ru": "Русский",
    "en": "Английский",
}


def setup_logging():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def load_template(template_path: pathlib.Path) -> str:
    return template_path.open(mode="r", encoding="utf-8").read()


def generate_abbr(length: int, lang: Lang) -> str:
    if lang == "ru":
        CHARS = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ"
    elif lang == "en":
        CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    else:
        raise ValueError("Invalid lang: %r", lang)
    return "".join(random.choice(CHARS) for _ in range(length))


def get_default_lang(chat_data: dict[str, t.Any]) -> Lang:
    return chat_data.get("abbr-lang", "ru")


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
    assert update.effective_chat
    assert context.chat_data is not None

    query = update.callback_query
    await query.answer()

    match query.data:
        case None:
            pass

        case s if s.startswith("abbr-length"):
            length = int(s.split(":")[-1])
            lang = get_default_lang(context.chat_data)
            await query.edit_message_text(generate_abbr(length, lang))
            assert query.message
            await update.effective_chat.unpin_all_messages()
            await update.effective_chat.pin_message(query.message.id)

        case s if s.startswith("abbr-lang"):
            new_lang = s.split(":")[-1]
            await query.edit_message_text(f"Выбрано: {LANGUAGES[new_lang]}")
            context.chat_data["abbr-lang"] = new_lang


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat

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


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat
    assert context.chat_data is not None

    current_lang = get_default_lang(context.chat_data)
    keyboard = [[
        telegram.InlineKeyboardButton(
            f"{'✔ ' if current_lang == code else ''}{title}",
            callback_data=f"abbr-lang:{code}",
        )
        for code, title in LANGUAGES.items()
    ]]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите язык:",
        reply_markup=reply_markup,
    )


def run_app():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler(["start", "help"], start_command))
    app.add_handler(CommandHandler("new", new_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.run_polling()


if __name__ == "__main__":
    setup_logging()
    run_app()
