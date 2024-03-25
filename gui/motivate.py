from functools import partial

from PyQt5.QtWidgets import QGridLayout, QProgressBar

from gui.group_box import GroupBox
from gui.utils import button
from src.elvenar import Elvenar, time
from datetime import timedelta


class HelpBox(GroupBox):

    Title = 'Motivation'
    Height = 22

    def __init__(self):
        super().__init__()
        self.Layout = self.create_layout()
        self.create_widgets()
        self.PBar = self.create_progress_bar()

    def update(self):
        elapsed_time = time() - Elvenar.LastMotivate
        self.PBar.setFormat(str(timedelta(seconds=round(24 * 60 * 60 - elapsed_time))))
        self.PBar.setValue(round(elapsed_time / (24 * 60 * 60) * 100))

    def create_layout(self) -> QGridLayout:
        self.setLayout(QGridLayout(self))
        self.set_margins()
        return self.layout()  # noqa

    def create_progress_bar(self) -> QProgressBar:
        pbar = QProgressBar(self)
        self.Layout.addWidget(pbar, 1, 0, 1, 2)
        return pbar

    def create_widgets(self):
        self.Layout.addWidget(button('help', partial(Elvenar.motivate, all_=False)), 0, 0)
        self.Layout.addWidget(button('help all', partial(Elvenar.motivate, all_=True)), 0, 1)
