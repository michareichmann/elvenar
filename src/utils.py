import telegram_send
import asyncio
from typing import Tuple
from time import time
import numpy as np


def send_notification(msg: str):
    asyncio.run(telegram_send.send(messages=[msg]))


def box2pos(box, xoff=.5, yoff=.5) -> Tuple[int, int]:
    return round(box.left + box.width * xoff), round(box.top + box.height * yoff)


def t2ts(t: str) -> float:
    if 'Min' in t:
        return time() + np.sum(np.array(t.strip('Min').split(':')).astype('i') * [60, 1])
    elif 'Std' in t:
        return time() + np.sum(np.array(t.strip('Std').split(':')).astype('i') * [60 * 60, 60])
