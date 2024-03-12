from time import sleep

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QHBoxLayout, QGridLayout

from gui.group_box import GroupBox
from gui.utils import *
from src.elvenar import Elvenar

Elvenar = Elvenar()
set_button_height(25)


class ToolBox(GroupBox):

    Header = []
    Title = 'Tool Collection'
    Height = 22

    def __init__(self):
        super().__init__()

        self.FarmButton = button('farm', self.farm)
        self.CollectFarmButton = button('collect + farm', partial(self.farm, 0, True))

        self.FarmingThread = FarmingThread(self)

        self.Layout = self.create_layout()
        self.create_widgets()

    def update(self):
        ...

    def format(self):
        ...

    # ----------------------------------
    # region LAYOUT & WIDGETS
    def create_layout(self) -> QHBoxLayout:
        self.setLayout(QHBoxLayout(self))
        self.layout().setContentsMargins(4, 4, 4, 4)
        return self.layout()  # noqa

    def create_widgets(self):
        self.create_tool_box()
        # self.create_time_select()

    def collect(self):
        Elvenar.go_to_game()
        Elvenar.collect()

    def start_production(self):
        Elvenar.go_to_game()
        Elvenar.start_production()

    def collect_start(self, i=0):
        self.collect()
        sleep(2)
        Elvenar.start_production(i)

    def farm(self, i=0, collect_first=False):
        self.FarmingThread.configure(i, collect_first)
        self.FarmButton.setEnabled(False)
        self.CollectFarmButton.setEnabled(False)

        self.FarmingThread.finished.connect(partial(self.FarmButton.setEnabled, True))
        self.FarmingThread.finished.connect(partial(self.CollectFarmButton.setEnabled, True))
        self.FarmingThread.start()

    def create_tool_box(self):
        layout = QGridLayout()
        layout.addWidget(button('collect', self.collect), 0, 0)
        layout.addWidget(label('test'), 0, 1, CEN)
        layout.addWidget(button('start production', self.start_production), 1, 0)
        layout.addWidget(button('collect + start', self.collect_start), 2, 0)
        layout.addWidget(self.FarmButton, 3, 0)
        layout.addWidget(self.CollectFarmButton, 4, 0)
        layout.addWidget(button('stop farming', self.FarmingThread.terminate), 4, 1)
        self.Layout.addLayout(layout)
    # endregion
    # ----------------------------------


class FarmingThread(QThread):

    Time = 0
    CollectAtStart = True

    def run(self):
        Elvenar.go_to_game()
        Elvenar.farm(FarmingThread.Time, FarmingThread.CollectAtStart)

    @staticmethod
    def configure(t, collect_at_start):
        FarmingThread.Time = t
        FarmingThread.CollectAtStart = collect_at_start
