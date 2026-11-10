import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from config import (
    BOT_TOKEN,
    CHANNEL_USERNAMES,
    DATA_DIR,
    RELEASE_DATETIME,
    SUCCESS_TEXT,
    UNSUBSCRIBED_TEXT_TEMPLATE,
    WAIT_TEXT,
    WELCOME_TEXT,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHECK_CALLBACK = "check_subscription"
SUBSCRIBERS_FILE = os.path.join(DATA_DIR, "subscribers.json")
SENT_FLAG_FILE = os.path.join(DATA_DIR, "materials_sent.flag")
WELCOME_IMAGE = Path(__file__).parent / "welcome.webp"


def load_subscribers() -> set[int]:
    try:
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


def save_subscriber(user_id: int) -> None:
    subscribers = load_subscribers()
    if user_id in subscribers:
        return
    subscribers.add(user_id)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(subscribers), f)


def build_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(f"📢 Открыть {chan}", url=f"https://t.me/{chan.lstrip('@')}")]
        for chan in CHANNEL_USERNAMES
    ]
    buttons.append([InlineKeyboardButton("✅ Проверить подписку", callback_data=CHECK_CALLBACK)])
    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open(WELCOME_IMAGE, "rb") as photo:
        await update.message.reply_photo(
            photo=photo, caption=WELCOME_TEXT, reply_markup=build_keyboard()
        )


async def get_missing_channels(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> list[str]:
    missing = []
    for channel in CHANNEL_USERNAMES:
        member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
        if member.status not in ("member", "administrator", "creator"):
            missing.append(channel)
    return missing


async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id

    try:
        missing = await get_missing_channels(context, user_id)
    except Exception:
        logger.exception("Не удалось проверить подписку для user_id=%s", user_id)
        await query.answer("Не получилось проверить подписку, попробуйте позже.", show_alert=True)
        return

    if not missing:
        await query.answer()
        if datetime.now(timezone.utc) >= RELEASE_DATETIME:
            await query.edit_message_caption(caption=SUCCESS_TEXT)
        else:
            save_subscriber(user_id)
            await query.edit_message_caption(caption=WAIT_TEXT)
    else:
        missing_list = "\n".join(f"• {chan}" for chan in missing)
        await query.answer(
            f"Не вижу подписку на:\n{missing_list}\n\nПодпишитесь и нажмите кнопку ещё раз.",
            show_alert=True,
        )


async def send_materials_to_all(context: ContextTypes.DEFAULT_TYPE) -> None:
    if os.path.exists(SENT_FLAG_FILE):
        logger.info("Материалы уже разосланы ранее, пропускаю.")
        return

    subscribers = load_subscribers()
    logger.info("Перепроверяю подписку и рассылаю материалы %s пользователям.", len(subscribers))
    for user_id in subscribers:
        try:
            missing = await get_missing_channels(context, user_id)
        except Exception:
            logger.exception("Не удалось перепроверить подписку user_id=%s", user_id)
            continue

        try:
            if not missing:
                await context.bot.send_message(chat_id=user_id, text=SUCCESS_TEXT)
            else:
                missing_list = "\n".join(f"• {chan}" for chan in missing)
                await context.bot.send_message(
                    chat_id=user_id,
                    text=UNSUBSCRIBED_TEXT_TEMPLATE.format(missing_list=missing_list),
                )
        except Exception:
            logger.exception("Не удалось отправить сообщение user_id=%s", user_id)

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SENT_FLAG_FILE, "w", encoding="utf-8") as f:
        f.write(datetime.now(timezone.utc).isoformat())


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern=f"^{CHECK_CALLBACK}$"))

    delay_seconds = (RELEASE_DATETIME - datetime.now(timezone.utc)).total_seconds()
    if delay_seconds > 0:
        application.job_queue.run_once(send_materials_to_all, when=delay_seconds)
    else:
        application.job_queue.run_once(send_materials_to_all, when=0)

    application.run_polling()


if __name__ == "__main__":
    main()
