import os
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]

# Список каналов через запятую, например "@chan1,@chan2,@chan3"
CHANNEL_USERNAMES = [
    chan.strip() for chan in os.environ["CHANNEL_USERNAMES"].split(",") if chan.strip()
]

# Ссылка на материалы
MATERIALS_LINK = os.environ["MATERIALS_LINK"]

# Папка для хранения списка подписчиков между перезапусками (нужен volume на Railway)
DATA_DIR = os.environ.get("DATA_DIR", ".")

# Дата и время рассылки материалов, например "2026-12-01T09:00:00"
RELEASE_TZ = os.environ.get("RELEASE_TZ", "Europe/Copenhagen")
RELEASE_DATETIME = datetime.fromisoformat(
    os.environ.get("RELEASE_DATETIME", "2026-12-01T09:00:00")
).replace(tzinfo=ZoneInfo(RELEASE_TZ))

CHANNELS_LIST_TEXT = "\n".join(f"• {chan}" for chan in CHANNEL_USERNAMES)

WELCOME_TEXT = (
    "Привет! Чтобы получить доступ к материалам, подпишитесь на все каналы ниже, "
    "а затем нажмите кнопку «Проверить подписку»:\n\n"
    f"{CHANNELS_LIST_TEXT}"
)

RELEASE_DATE_HUMAN = RELEASE_DATETIME.strftime("%d.%m.%Y")

WAIT_TEXT = (
    "Отлично, подписка подтверждена! Материалы придут вам сюда же, в этот чат, "
    f"{RELEASE_DATE_HUMAN}. Важно: не отписывайтесь от каналов до этого дня — "
    f"{RELEASE_DATE_HUMAN} бот ещё раз проверит подписку, и если вы отпишетесь, "
    "материалы не придут."
)

SUCCESS_TEXT = f"Спасибо за подписку! Вот ваши материалы:\n{MATERIALS_LINK}"

UNSUBSCRIBED_TEXT_TEMPLATE = (
    "Кажется, вы отписались от некоторых каналов, поэтому не можем прислать материалы:\n"
    "{missing_list}\n\n"
    "Подпишитесь заново и нажмите «Проверить подписку» в сообщении выше."
)
