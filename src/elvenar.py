import re
from subprocess import call, getoutput
from time import sleep

import ffmpeg
from PIL import Image
from pytesseract import image_to_string

from src.utils import *
from user_input.keys import Keys
from user_input.mouse import Mouse
from utils.classes import NumStr
from utils.helpers import play, Dir, ON, write_log, Path, do_pickle


# ------------------------------
# region helper functions
def locate_all_(pic, confidence=.99):
    from pyautogui import locateAllOnScreen
    try:
        return list(locateAllOnScreen(str(pic), confidence=confidence))
    except Exception as e:
        print(pic, e)
        return []


def locate_all(*pics, confidence=.99):
    return sum((locate_all_(p, confidence) for p in pics), start=[])


def locate(pic, confidence=.99, region=None):
    from pyautogui import locateOnScreen, locate, screenshot
    try:
        return locateOnScreen(str(pic), confidence=confidence) if region is None else locate(str(pic), screenshot(region=region), confidence=confidence)
    except Exception as e:
        print(pic, e)
        return None


def img2str(img: Image, threshold=180, inverted=False, save=False, convert=False, sub='[^a-zA-Z0-9.:]+'):
    if convert or inverted:
        x = np.array(img.convert('L'))  # grayscale img as array
        black, white = (x >= threshold, x < threshold) if inverted else (x <= threshold, x > threshold)
        x[black] = 0
        x[white] = 255
        img = Image.fromarray(x)
    if save:
        img.save(Dir.joinpath('logs', 'test.png'))
    return re.sub(sub, '', image_to_string(img))
# endregion
# ------------------------------


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
    Sound = ON
    Volume = 10
    Paused = False

    LMPath = Dir.joinpath('config', 'last-motivate.pickle')
    LastMotivate = do_pickle(LMPath, time)

    def __init__(self):
        pass

    @staticmethod
    def increment(*_a, **_kw):
        Elvenar.SelectedInd = (Elvenar.SelectedInd + 1) % 6

    @staticmethod
    def decrement():
        Elvenar.SelectedInd = max(0, Elvenar.SelectedInd - 1)

    @staticmethod
    def t_str():
        return Elvenar.TStrings[Elvenar.SelectedInd]

    @staticmethod
    def pic(*names, ext='png'):
        lst = list(names)
        lst[-1] = f'{lst[-1].split(".")[0]}.{ext}'
        return Elvenar.FigDir.joinpath(*lst)

    @staticmethod
    def reset():
        Elvenar.NIter = 0
        Elvenar.T0 = None
        Elvenar.CollectedTools = 0

    @staticmethod
    def select_time(t: int):
        Elvenar.SelectedInd = t

    @staticmethod
    def change_sound():
        Elvenar.Sound = not Elvenar.Sound

    @staticmethod
    def activate():
        box = locate(Elvenar.pic('guild'))
        if box is not None:
            Elvenar.Mouse.left_click(*(box.left - 10, box.top))
        else:
            raise ValueError('Error activating game')

    @staticmethod
    def go_to_city():
        call('wmctrl -a "Google Chrome"', shell=True)
        sleep(.3)
        box = locate(Elvenar.pic('browser-icon'), region=(0, 0, 2000, 100), confidence=.7)
        if box is not None:
            Elvenar.Mouse.left_click(box.left + box.width, box.top + box.height // 2)
        Elvenar.Keys.tap('c', wait=.5)
        Elvenar.Keys.press_esc(wait=.5)

    @staticmethod
    def zoom_in(n=5):
        Elvenar.Keys.tap('+', n=n)

    @staticmethod
    def zoom_out(n=5):
        Elvenar.Keys.tap('-', n=n)

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
        Elvenar.update_tool_count(old_count)

    @staticmethod
    def start_production(pos):
        Elvenar.Mouse.left_click(*pos, wait=1)
        Elvenar.Keys.tap(str(Elvenar.SelectedInd + 1), wait=.2)
        Elvenar.T0 = time()

    @staticmethod
    def pause():
        Elvenar.Paused = not Elvenar.Paused

    @staticmethod
    def farm(collect_at_start=False):
        Elvenar.NIter = 0
        Elvenar.CollectedTools = 0
        while True:
            active_win = getoutput('xprop -root | grep _NET_ACTIVE_WINDOW | head -1 | cut -f5 -d " "')
            if Elvenar.NIter > 0:  # assume that the game is open upon first usage
                sleep(2)
                while Elvenar.Paused:
                    sleep(1)
                Elvenar.go_to_city()
                sleep(8)  # it may take some time until the game refreshes
            Elvenar.activate()
            pos = Elvenar.find_workshops()
            if len(pos) > 0:
                if collect_at_start or Elvenar.NIter > 0:
                    Elvenar.collect(*pos)
                    sleep(1)
                Elvenar.start_production(pos[0])
            call(f'wmctrl -ia {active_win}', shell=True)
            sleep(Elvenar.Times[Elvenar.SelectedInd] * 60 - 21)
            Elvenar.play_sound(Dir.joinpath('audio', 'bells.mp3'))

    @staticmethod
    def play_sound(f: Path):
        t = float(ffmpeg.probe(f)['format']['duration'])
        if t > 10:
            raise ValueError('sound file too long!')
        sleep(10 - t)
        if Elvenar.Sound:
            play(f, Elvenar.Volume)
        else:
            sleep(t)

    @staticmethod
    def find_workshops(confidence=.8):
        return Elvenar.find_buildings(Elvenar.FigDir.joinpath('ws'), confidence)

    @staticmethod
    def find_residences(confidence=.8):
        return Elvenar.find_buildings(Elvenar.FigDir.joinpath('rb'), confidence)

    @staticmethod
    def find_buildings(p: Path, confidence=.8):
        try:
            v = locate_all(*p.glob('*.png'), confidence=confidence)
            pos = np.array([(int(b.left + b.width / 2), int(b.top + b.height)) for b in v])
            pos = pos[np.argsort(np.linalg.norm(pos, axis=1))]  # sort by distance to offspring
            d = np.concatenate([[99], np.linalg.norm(np.diff(pos, axis=0), axis=1)])  # distance between the neighbouring points
            return pos[d > 5]
        except Exception as e:
            print(e)
            return []

    @staticmethod
    def motivate(all_=True):
        v = [1]
        while len(v):
            v = locate_all(*(Elvenar.pic(f'hands{i}') for i in ['', '-gold']), confidence=.99)
            for pos in [(int(b.left + b.width / 2), int(b.top + b.height / 2)) for b in v]:
                Elvenar.Mouse.left_click(*pos, wait=.5)
                for s in ['culture', 'money', 'construct']:
                    box = locate(Elvenar.pic(s), confidence=.9)
                    if box is not None:
                        Elvenar.Mouse.left_click(box.left, box.top, wait=.3)
                        break
            if not all_:
                v = []
            else:
                sleep(.5)
                Elvenar.Keys.press_right(wait=2)
        if all_:
            Elvenar.save_last_motivate()

    @staticmethod
    def save_last_motivate():
        Elvenar.LastMotivate = do_pickle(Elvenar.LMPath, lambda: time() - 60 * 60, redo=True)

    @staticmethod
    def read_tool_count(threshold=170):
        try:
            from pyautogui import screenshot
            box = locate(Elvenar.pic('black-tools'))
            r = np.array([box.left + box.width, box.top, int(2.5 * box.width), box.height]).tolist()
            return NumStr(img2str(screenshot(region=r), threshold, inverted=True, sub='[^KMG0-9.]+'))
        except Exception as err:
            print(err)

    @staticmethod
    def update_tool_count(old_cnt):
        try:
            new_count = Elvenar.read_tool_count()
            if Elvenar.NIter and old_cnt - new_count > 3 * Elvenar.CollectedTools / Elvenar.NIter:
                write_log(f'Strange tool count: old: {old_cnt}, new {new_count}, avr: {Elvenar.CollectedTools / Elvenar.NIter:.1f}')
            elif new_count > old_cnt:
                Elvenar.CollectedTools = NumStr(Elvenar.CollectedTools + new_count - old_cnt)
        except Exception as err:
            print(err)

    @staticmethod
    def read_construction_timers():
        from pyautogui import screenshot
        Elvenar.activate()
        box = locate(Elvenar.pic('builder'), confidence=.9)
        if box is not None:
            Elvenar.Mouse.left_click(*box2pos(box), wait=1)
            regions = [np.array([box.left - box.width * 2.5, box.top, box.width * 2.5, box.height]).astype('i') for box in locate_all(Elvenar.pic('build-t'))]
            times = [img2str(screenshot(region=r.tolist())) for r in regions]
            Elvenar.Keys.press_esc()
            return filter(lambda x: 'Std' in x or 'Min' in x, times)
        return []

