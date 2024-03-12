from time import sleep

import numpy as np

from user_input.keys import Keys
from user_input.mouse import Mouse
from utils.helpers import say, Dir


class Elvenar:

    Start = (860, 544)
    End = (415, 770)
    WPos = [(720, 543), (920, 543)]
    Times = {5: '5min', 15: '15min', 60: '1hr', 3 * 60: '3hrs', 9 * 60: '9hrs', 24 * 60: '1d'}  # in minutes

    def __init__(self):

        self.Mouse = Mouse()
        self.Keys = Keys()

    def go_to_game(self):
        self.Mouse.left_click(0, 1078, wait=.2)
        # self.Keys.press_alt_tab(wait=.4)

    def zoom_in(self, n=5):
        self.go_to_game()  # only for testing
        self.Keys.tap('+', n=n)

    def zoom_out(self, n=5):
        self.Keys.tap('-', n=n)

    def print_mouse_pos(self):
        print('({:1.0f}, {:1.0f})'.format(*self.Mouse.position()))

    def collect(self):
        self.Mouse.press(*self.Start)
        for p in np.linspace(self.Start, self.End, 8):
            self.Mouse.move(*p, wait=.1)
        self.Mouse.release(*self.End)

    def start_production(self, i=0):
        self.Mouse.left_click(*self.Start, wait=.5)
        self.Mouse.left_click(*self.WPos[i])

    def farm(self, i, collect_first=True):
        j = 0
        while True:
            if collect_first or j > 0:
                self.collect()
                sleep(2)
            self.start_production(i)
            sleep(list(Elvenar.Times.keys())[i] * 60 - 10)
            say(Dir.joinpath('audio', '15sec.mp3'), '15 seconds left!')
            sleep(15)
            print(f'\r{j}', end='')
            j += 1

    def motivate(self):
        ...
