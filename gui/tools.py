from datetime import timedelta
from time import time

import numpy as np

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QProgressBar

from gui.group_box import GroupBox
from gui.utils import *
from src.elvenar import Elvenar
from utils.helpers import Dir, write_log

FigDir = Dir.joinpath('figures')
Elvenar = Elvenar()


class ToolBox(GroupBox):

    Header = []
    Title = 'Tool Collection'
    Height = 22

    def __init__(self):
        super().__init__(QVBoxLayout)

        self.FarmButton = button('start', self.farm)
        self.CollectFarmButton = button('coll && start', partial(self.farm, True))
        self.TCheckBoxes = self.create_t_check_boxes()
        self.InfoLabel = label('x')
        self.ToolLabel = label('0')
        self.FLabel = self.create_f_label()

        self.FarmingThread = FarmingThread(self)

        self.create_tool_box()
        self.PBar: QProgressBar = self.create_progress_bar()

    def update(self):
        if Elvenar.T0 is not None:
            duration = timedelta(minutes=Elvenar.Times[Elvenar.SelectedInd])
            elapsed_time = timedelta(seconds=int(np.round(time() - Elvenar.T0)))
            if elapsed_time < duration:
                self.PBar.setFormat(str(duration - elapsed_time))
                self.PBar.setValue(int(np.round(elapsed_time / duration * 100)))
            else:
                self.PBar.reset()
        self.InfoLabel.setText(f'{Elvenar.NIter}')
        self.ToolLabel.setText(f'{Elvenar.CollectedTools}')
        self.FLabel.setText(f'f = {Elvenar.t_str()}')

    def format(self):
        ...

    @property
    def tool_select(self):
        return next((i for i, cb in enumerate(self.TCheckBoxes) if cb.isChecked()), 0)

    # ----------------------------------
    # region LAYOUT & WIDGETS
    def create_progress_bar(self):
        pbar = QProgressBar(self)
        self.Layout.addWidget(pbar)
        return pbar

    def farm(self, collect_at_start=False):

        self.FarmButton.setEnabled(False)
        self.CollectFarmButton.setEnabled(False)

        FarmingThread.CollectAtStart = collect_at_start
        self.FarmingThread.finished.connect(partial(self.FarmButton.setEnabled, True))
        self.FarmingThread.finished.connect(partial(self.CollectFarmButton.setEnabled, True))
        self.FarmingThread.finished.connect(Elvenar.reset)
        self.FarmingThread.finished.connect(self.PBar.reset)
        self.FarmingThread.start()

    def test(self):
        print('hello')

    def create_tool_box(self):
        layout = QGridLayout()
        # layout.addWidget(button('test', self.test), 0, 0)
        layout.addWidget(self.FLabel, 0, 0)
        sound_button = SoundButton(Elvenar.change_sound, Elvenar.FigDir.joinpath('sound.svg'), Elvenar.FigDir.joinpath('sound-off.svg'), size=(20, 20))
        layout.addWidget(sound_button, 0, 1, RIGHT)
        layout.addWidget(self.FarmButton, 1, 0)
        layout.addWidget(self.CollectFarmButton, 2, 0)
        layout.addWidget(PauseButton(Elvenar.pause), 1, 1)
        layout.addWidget(button('stop', self.FarmingThread.terminate), 2, 1)
        layout.addWidget(label('Iterations:'), 4, 0, RIGHT)
        layout.addWidget(self.InfoLabel, 4, 1, LEFT)
        layout.addWidget(label('Collected:'), 5, 0, RIGHT)
        layout.addWidget(self.ToolLabel, 5, 1, LEFT)
        self.Layout.addLayout(layout)

    @staticmethod
    def create_f_label():
        lb = label(f'f = {Elvenar.t_str()}')
        lb.mousePressEvent = Elvenar.increment
        return lb

    def create_t_selector(self):
        layout = QGridLayout()
        layout.addWidget(fig_label(FigDir.joinpath('time.png')), 0, 1, CEN)
        layout.addWidget(fig_label(FigDir.joinpath('time.png')), 0, 4, CEN)
        for i in range(6):
            layout.addWidget(label(Elvenar.TStrings[i]), i % 3 + 1, 1 if i < 3 else 4, RIGHT if i < 3 else LEFT)
            layout.addWidget(fig_label(FigDir.joinpath(f'{i}.png'), scale=.5), i % 3 + 1, 0 if i < 3 else 5, CEN)
            layout.addWidget(self.TCheckBoxes[i], i % 3 + 1, 2 if i < 3 else 3)
        return layout

    def create_t_check_boxes(self):
        self.TCheckBoxes = [check_box() for _ in range(6)]
        self.TCheckBoxes[0].setChecked(True)

        def uncheck_others(ibox):
            [cb.setChecked(False) for cb in self.TCheckBoxes if ibox.isChecked() and cb.isChecked() and ibox != cb]

        for box in self.TCheckBoxes:
            box.toggled.connect(partial(uncheck_others, box))
            box.toggled.connect(lambda: Elvenar.select_time(self.tool_select))
        return self.TCheckBoxes
    # endregion
    # ----------------------------------


class FarmingThread(QThread):

    CollectAtStart = True

    def run(self):
        try:
            Elvenar.farm(collect_at_start=FarmingThread.CollectAtStart)
        except Exception as err:
            import traceback
            print(err)
            write_log(traceback.format_exc())
