import telegram_send
import asyncio


def send_notification(msg: str):
    asyncio.run(telegram_send.send(messages=[msg]))
