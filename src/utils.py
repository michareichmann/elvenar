import telegram_send
import asyncio
from typing import Tuple


def send_notification(msg: str):
    asyncio.run(telegram_send.send(messages=[msg]))


def box2pos(box, xoff=.5, yoff=.5) -> Tuple[int, int]:
    return round(box.left + box.width * xoff), round(box.top + box.height * yoff)
