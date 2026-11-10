import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]

# Список каналов через запятую, например "@chan1,@chan2,@chan3"
CHANNEL_USERNAMES = [
    chan.strip() for chan in os.environ["CHANNEL_USERNAMES"].split(",") if chan.strip()
]

# Ссылка, которую бот присылает подписчикам
MATERIALS_LINK = os.environ["MATERIALS_LINK"]

CHANNELS_LIST_TEXT = "\n".join(f"• {chan}" for chan in CHANNEL_USERNAMES)

WELCOME_TEXT = (
    "Привет! Чтобы получить доступ к материалам, подпишитесь на все каналы ниже, "
    "а затем нажмите кнопку «Проверить подписку»:\n\n"
    f"{CHANNELS_LIST_TEXT}"
)

SUCCESS_TEXT = f"Спасибо за подписку! Вот ваши материалы:\n{MATERIALS_LINK}"
