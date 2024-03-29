from functools import partial

from PyQt5.QtWidgets import QGridLayout, QProgressBar

from gui.group_box import GroupBox
from gui.utils import button, TmpDir
from src.elvenar import Elvenar, time
from datetime import timedelta
from src.utils import send_notification
from utils.helpers import do_pickle


class HelpBox(GroupBox):

    Title = 'Motivation'
    TDay = 24 * 60 * 60

    PicklePath = TmpDir.joinpath('last-motivate.pickle')
    LastMotivate = do_pickle(PicklePath, time)

    def __init__(self):
        super().__init__(QGridLayout)

        self.create_widgets()
        self.PBar = self.create_progress_bar()

        self.Notified = False

    def update(self):
        elapsed_time = time() - self.LastMotivate
        self.PBar.setFormat(str(timedelta(seconds=round(self.TDay - elapsed_time))) if elapsed_time < self.TDay else 'Ready')
        self.PBar.setValue(round(elapsed_time / self.TDay * 100))
        if elapsed_time > self.TDay and not self.Notified:
            send_notification('ready to motivate')
            self.Notified = True

    def create_progress_bar(self) -> QProgressBar:
        pbar = QProgressBar(self)
        self.Layout.addWidget(pbar, 1, 0, 1, 2)
        return pbar

    def help_all(self):
        Elvenar.motivate(all_=True)
        self.Notified = False
        do_pickle(self.PicklePath, lambda: time() - 60 * 60, redo=True)

    def create_widgets(self):
        self.Layout.addWidget(button('help', partial(Elvenar.motivate, all_=False)), 0, 0)
        self.Layout.addWidget(button('help all', self.help_all), 0, 1)
