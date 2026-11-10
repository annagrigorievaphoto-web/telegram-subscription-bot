import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from config import BOT_TOKEN, CHANNEL_USERNAMES, SUCCESS_TEXT, WELCOME_TEXT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHECK_CALLBACK = "check_subscription"


def build_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(f"📢 Открыть {chan}", url=f"https://t.me/{chan.lstrip('@')}")]
        for chan in CHANNEL_USERNAMES
    ]
    buttons.append([InlineKeyboardButton("✅ Проверить подписку", callback_data=CHECK_CALLBACK)])
    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_TEXT, reply_markup=build_keyboard())


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
        await query.edit_message_text(SUCCESS_TEXT)
    else:
        missing_list = "\n".join(f"• {chan}" for chan in missing)
        await query.answer(
            f"Не вижу подписку на:\n{missing_list}\n\nПодпишитесь и нажмите кнопку ещё раз.",
            show_alert=True,
        )


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern=f"^{CHECK_CALLBACK}$"))
    application.run_polling()


if __name__ == "__main__":
    main()
