from functools import partial

from PyQt5.QtWidgets import QGridLayout

from gui.group_box import GroupBox
from gui.utils import button
from src.elvenar import Elvenar


class HelpBox(GroupBox):

    Title = 'Motivation'
    Height = 22

    def __init__(self):
        super().__init__()
        self.Layout = self.create_layout()
        self.create_widgets()

    def create_layout(self) -> QGridLayout:
        self.setLayout(QGridLayout(self))
        self.set_margins()
        return self.layout()  # noqa

    def create_widgets(self):
        self.Layout.addWidget(button('help', partial(Elvenar.motivate, all_=False)), 0, 0)
        self.Layout.addWidget(button('help all', partial(Elvenar.motivate, all_=True)), 0, 1)
