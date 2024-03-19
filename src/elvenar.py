import re
from time import sleep, time

import numpy as np
from PIL import Image

from user_input.keys import Keys
from user_input.mouse import Mouse
from utils.helpers import say, Dir
from utils.classes import NumStr

from subprocess import call, getoutput


class Elvenar:

    FigDir = Dir.joinpath('figures')

    Times = [5, 15, 60, 3 * 60, 9 * 60, 24 * 60]  # in minutes
    TStrings = ['5 min', '15 min', '1 hr', '3 hrs', '9 hrs', '1 d']
    NIter = 0
    CollectedTools = 0
    T0 = None
    Mouse = Mouse()
    Keys = Keys()
    SelectedInd = 0

    def __init__(self):
        pass

    @staticmethod
    def reset():
        Elvenar.NIter = 0
        Elvenar.T0 = None
        Elvenar.CollectedTools = 0

    @staticmethod
    def select_time(t: int):
        Elvenar.SelectedInd = t

    @staticmethod
    def activate():
        box = Elvenar.locate(Elvenar.FigDir.joinpath('path.png'))
        Elvenar.Mouse.left_click(*(box.left, box.top) if box is not None else (0, 2222), wait=.2)

    @staticmethod
    def go_to_city():
        call('wmctrl -a "Google Chrome"', shell=True)
        sleep(.1)
        box = Elvenar.locate(Elvenar.FigDir.joinpath('browser-icon.png'), region=(0, 0, 2000, 100), confidence=.8)
        Elvenar.Mouse.left_click(box.left + box.width, box.top + box.height // 2)
        Elvenar.Keys.tap('c', wait=.5)
        Elvenar.activate()

    def zoom_in(self, n=5):
        self.go_to_city()  # only for testing
        self.Keys.tap('+', n=n)

    def zoom_out(self, n=5):
        self.Keys.tap('-', n=n)

    def print_mouse_pos(self):
        print('({:1.0f}, {:1.0f})'.format(*self.Mouse.position()))

    @staticmethod
    def collect(*pos, wait=.1):
        old_count = Elvenar.read_tool_count()
        Elvenar.Mouse.press(*pos[0], wait=wait)
        for p in pos:
            Elvenar.Mouse.move(*p, wait=wait)
        Elvenar.Mouse.release(*pos[-1])
        Elvenar.NIter += 1
        sleep(2)
        Elvenar.CollectedTools = NumStr(Elvenar.CollectedTools + Elvenar.read_tool_count() - old_count)

    @staticmethod
    def start_production(pos):
        Elvenar.Mouse.left_click(*pos, wait=.5)
        Elvenar.Mouse.left_click(*Elvenar.find_tool_time())
        Elvenar.T0 = time()

    def farm(self, collect_at_start=False):
        Elvenar.NIter = 0
        Elvenar.CollectedTools = 0
        while True:
            active_win = getoutput('xprop -root | grep _NET_ACTIVE_WINDOW | head -1 | cut -f5 -d " "')
            Elvenar.go_to_city()
            sleep(10)  # it may take some time until the game refreshes
            pos = self.find_workshops()
            if len(pos) > 0:
                if collect_at_start or Elvenar.NIter > 0:
                    self.collect(*pos)
                    sleep(2)
                self.start_production(pos[0])
                # self.Mouse.move(0, 600)  # move mouse away for pic identification
            call(f'wmctrl -ia {active_win}', shell=True)
            sleep(Elvenar.Times[Elvenar.SelectedInd] * 60 - 14)
            say(Dir.joinpath('audio', '15sec.mp3'), '15 seconds left!')
            sleep(5)

    @staticmethod
    def locate_all_(pic, confidence=.99):
        from pyautogui import locateAllOnScreen
        try:
            return list(locateAllOnScreen(str(pic), confidence=confidence))
        except Exception as e:
            print(e)
            return []

    @staticmethod
    def locate_all(*pics, confidence=.99):
        return sum((Elvenar.locate_all_(p, confidence) for p in pics), start=[])

    @staticmethod
    def locate(pic, confidence=.99, region=None):
        from pyautogui import locateOnScreen, locate, screenshot
        try:
            return locateOnScreen(str(pic), confidence=confidence) if region is None else locate(str(pic), screenshot(region=region), confidence=confidence)
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def find_workshops(confidence=.85):
        try:
            v = Elvenar.locate_all(*Elvenar.FigDir.joinpath('ws').glob('*.png'), confidence=confidence)
            pos = [(int(b.left + b.width / 2), int(b.top + b.height)) for b in v]
            return [p for i, p in enumerate(pos) if i == 0 or abs(p[0] - pos[i - 1][0] + p[1] - pos[i - 1][1]) > 5]  # remove duplicates
        except Exception as e:
            print(e)
            return []

    @staticmethod
    def find_tool_time():
        box = Elvenar.locate(Elvenar.FigDir.joinpath('tool-times', f'{Elvenar.SelectedInd}.png'), confidence=.8)
        return (0, 0) if box is None else box.left + box.width, box.top + box.height

    @staticmethod
    def motivate():
        v = Elvenar.locate_all(*(Elvenar.FigDir.joinpath(f'hands{i}.png') for i in ['', '-gold']), confidence=.99)
        for pos in [(int(b.left + b.width / 2), int(b.top + b.height / 2)) for b in v]:
            Elvenar.Mouse.left_click(*pos, wait=.5)
            for pic in [Elvenar.FigDir.joinpath(f'{i}.png') for i in ['culture', 'money', 'construct']]:
                box = Elvenar.locate(pic, confidence=.9)
                if box is not None:
                    Elvenar.Mouse.left_click(box.left, box.top, wait=.3)
                    break

    @staticmethod
    def read_tool_count(threshold=150):
        try:
            from pytesseract import image_to_string
            from pyautogui import screenshot
            box = Elvenar.locate(Elvenar.FigDir.joinpath('black-tools.png'))
            r = np.array([box.left + box.width, box.top, int(2.5 * box.width), box.height]).tolist()
            x = np.array(screenshot(region=r).convert('L'))  # grayscale img as array
            black, white = x >= threshold, x < threshold
            x[black] = 0
            x[white] = 255
            return NumStr(re.sub('[^KMG0-9.]+', '', image_to_string(Image.fromarray(x))))
        except Exception as err:
            print(err)


