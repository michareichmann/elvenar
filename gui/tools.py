from time import sleep, time

import numpy as np
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QHBoxLayout, QGridLayout, QVBoxLayout, QProgressBar

from gui.group_box import GroupBox
from gui.utils import *
from src.elvenar import Elvenar
from utils.helpers import Dir

FigDir = Dir.joinpath('figures')
Elvenar = Elvenar()
set_button_height(25)


class ToolBox(GroupBox):

    Header = []
    Title = 'Tool Collection'
    Height = 22

    def __init__(self):
        super().__init__()

        self.FarmButton = button('farm', self.farm)
        self.CollectFarmButton = button('collect + farm', partial(self.farm, True))
        self.TCheckBoxes = self.create_t_check_boxes()
        self.InfoBox = line_edit()

        self.FarmingThread = FarmingThread(self)
        self.T0 = None
        self.Duration = None

        self.Layout = self.create_layout()
        self.create_upper_box()
        self.PBar: QProgressBar = self.create_progress_bar()

    def update(self):
        if self.T0 is not None:
            self.PBar.setValue(int(np.round((time() - self.T0) / self.Duration * 100)))

    def format(self):
        ...

    @property
    def tool_select(self):
        return next((i for i, cb in enumerate(self.TCheckBoxes) if cb.isChecked()), 0)

    # ----------------------------------
    # region LAYOUT & WIDGETS
    def create_layout(self) -> QVBoxLayout:
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(4, 4, 4, 4)
        return self.layout()  # noqa

    def create_upper_box(self):
        layout = QHBoxLayout()
        layout.addLayout(self.create_tool_box())
        layout.addLayout(self.create_t_selector())
        self.Layout.addLayout(layout)

    def create_progress_bar(self):
        pbar = QProgressBar(self)
        self.Layout.addWidget(pbar)
        return pbar

    def create_widgets(self):
        self.create_tool_box()
        self.create_t_selector()

    def collect(self):
        Elvenar.go_to_game()
        Elvenar.collect()

    def start_production(self):
        Elvenar.go_to_game()
        Elvenar.start_production(self.tool_select)

    def collect_start(self):
        self.collect()
        sleep(2)
        Elvenar.start_production(self.tool_select)

    def farm(self, collect_first=False):
        self.T0 = time()
        self.Duration = Elvenar.Times[self.tool_select] * 60

        self.FarmingThread.configure(self.tool_select, collect_first)
        self.FarmButton.setEnabled(False)
        self.CollectFarmButton.setEnabled(False)

        self.FarmingThread.finished.connect(partial(self.FarmButton.setEnabled, True))
        self.FarmingThread.finished.connect(partial(self.CollectFarmButton.setEnabled, True))
        self.FarmingThread.start()

    def test(self):
        self.InfoBox.clear()
        self.InfoBox.insert('Hello')

    def create_tool_box(self):
        layout = QGridLayout()
        layout.addWidget(button('test', self.test), 0, 1)
        layout.addWidget(self.FarmButton, 0, 0)
        layout.addWidget(self.CollectFarmButton, 1, 0)
        layout.addWidget(button('stop farming', self.FarmingThread.terminate), 1, 1)
        layout.addWidget(label('Info:'), 2, 0, RIGHT)
        layout.addWidget(self.InfoBox, 2, 1, RIGHT)
        return layout

    def create_t_selector(self):
        layout = QGridLayout()
        layout.addWidget(fig_label(FigDir.joinpath('time.png')), 0, 1, CEN)
        layout.addWidget(fig_label(FigDir.joinpath('time.png')), 0, 4, CEN)
        for i in range(6):
            layout.addWidget(label(Elvenar.TStrings[i]), i % 3 + 1, 1 if i < 3 else 4, RIGHT if i < 3 else LEFT)
            layout.addWidget(fig_label(FigDir.joinpath(f'{i}.png'), scale=.5), i % 3 + 1, 0 if i < 3 else 5, CEN)
            layout.addWidget(self.TCheckBoxes[i], i % 3 + 1, 2 if i < 3 else 3)
        return layout

    # endregion
    # ----------------------------------
    def create_t_check_boxes(self):
        self.TCheckBoxes = [check_box() for _ in range(6)]
        self.TCheckBoxes[0].setChecked(True)

        def uncheck_others(ibox):
            [cb.setChecked(False) for cb in self.TCheckBoxes if ibox.isChecked() and cb.isChecked() and ibox != cb]

        for box in self.TCheckBoxes:
            box.toggled.connect(partial(uncheck_others, box))
        return self.TCheckBoxes


class FarmingThread(QThread):

    # TODO: change time while in loop
    Time = 0
    CollectAtStart = True

    def run(self):
        Elvenar.go_to_game()
        Elvenar.farm(FarmingThread.Time, FarmingThread.CollectAtStart)

    @staticmethod
    def configure(t, collect_at_start):
        FarmingThread.Time = t
        FarmingThread.CollectAtStart = collect_at_start
