import logging
import os
import random

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ["TELEGRAM_TOKEN"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


class AbbrException(Exception):
    pass


class InvalidArgument(AbbrException):
    pass


def generate_abbr(length: int) -> str:
    SYMBOLS = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ"
    return "".join(random.choice(SYMBOLS) for _ in range(length))


def parse_next_args(args: list) -> int:
    args = list(args)
    try:
        length = int(args.pop(0))
        if not (5 >= length >= 3):
            raise InvalidArgument("Размер должен быть от 3 до 5")
    except IndexError:
        length = 3
    except ValueError:
        raise InvalidArgument("Размер должен быть числом")
    return length


async def next_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat
    assert update.message

    try:
        length = parse_next_args(context.args or [])
    except InvalidArgument as exception:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.message.id,
            text=str(exception),
        )
        return None

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=generate_abbr(length),
    )


def run_application():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("next", next_command))
    application.run_polling()


if __name__ == "__main__":
    run_application()
