from time import sleep, time

from user_input.keys import Keys
from user_input.mouse import Mouse
from utils.helpers import say, Dir


class Elvenar:

    FigDir = Dir.joinpath('figures')

    Times = [5, 15, 60, 3 * 60, 9 * 60, 24 * 60]  # in minutes
    TStrings = ['5 min', '15 min', '1 hr', '3 hrs', '9 hrs', '1 d']
    NIter = 0
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

    @staticmethod
    def select_time(t: int):
        Elvenar.SelectedInd = t

    def go_to_game(self):
        # TODO find smarter solution (open chrome with specific tab?)
        self.Mouse.left_click(0, 1078, wait=.2)
        # self.Keys.press_alt_tab(wait=.4)

    def zoom_in(self, n=5):
        self.go_to_game()  # only for testing
        self.Keys.tap('+', n=n)

    def zoom_out(self, n=5):
        self.Keys.tap('-', n=n)

    def print_mouse_pos(self):
        print('({:1.0f}, {:1.0f})'.format(*self.Mouse.position()))

    @staticmethod
    def collect(*pos, wait=.1):
        Elvenar.Mouse.press(*pos[0], wait=wait)
        for p in pos:
            Elvenar.Mouse.move(*p, wait=wait)
        Elvenar.Mouse.release(*pos[-1])
        Elvenar.NIter += 1

    @staticmethod
    def start_production(pos):
        Elvenar.Mouse.left_click(*pos, wait=.5)
        Elvenar.Mouse.left_click(*Elvenar.find_tool_time())
        Elvenar.T0 = time()

    def farm(self, collect_at_start=False):
        Elvenar.NIter = 0
        while True:
            pos = self.find_workshops()
            if len(pos) > 0:
                if collect_at_start or Elvenar.NIter > 0:
                    self.collect(*pos)
                    sleep(2)
                self.start_production(pos[0])
                self.Mouse.move(0, 600)  # move mouse away for pic identification
            sleep(Elvenar.Times[Elvenar.SelectedInd] * 60 - 10)
            say(Dir.joinpath('audio', '15sec.mp3'), '15 seconds left!')
            sleep(15)

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
    def locate(pic, confidence=.99):
        from pyautogui import locateOnScreen
        try:
            return locateOnScreen(str(pic), confidence=confidence)
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

