from PyQt5.QtWidgets import QHBoxLayout, QProgressBar

from gui.group_box import GroupBox
from gui.utils import ResetButton
from src.utils import send_notification
from utils.helpers import Dir, time, do_pickle, timedelta


class GoodsBox(GroupBox):

    Title = 'Goods'
    TProd = 3 * 60 ** 2  # 3 hrs
    TFPath = Dir.joinpath('config', 'goods-finished.pickle')

    def __init__(self):
        super().__init__(QHBoxLayout)

        self.TFinish = do_pickle(self.TFPath, lambda: time() + self.TProd)

        self.PBar = self.create_progress_bar()
        self.create_update_button()

        self.Notified = False

    def update(self):
        t = round(self.TProd - (self.TFinish - time()))
        self.PBar.setFormat(str(timedelta(seconds=self.TProd - t)) if t < self.TProd else '')
        self.PBar.setValue(t)
        if self.TProd < t < self.TProd + 5 * 60 and not self.Notified:
            send_notification('goods are ready')
            self.Notified = True

    def create_progress_bar(self) -> QProgressBar:
        pbar = QProgressBar(self)
        pbar.setRange(0, self.TProd)
        self.Layout.addWidget(pbar)
        return pbar

    def reset(self):
        self.TFinish = do_pickle(self.TFPath, lambda: time() + self.TProd, redo=True)
        self.Notified = False

    def create_update_button(self):
        self.Layout.addWidget(ResetButton(self.reset))
