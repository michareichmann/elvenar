from gui.group_box import GroupBox
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QProgressBar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from gui.utils import ResetButton, CEN
from src.elvenar import Elvenar
from utils.helpers import Dir, do_pickle, time, timedelta
from src.utils import send_notification, t2ts


class Builder(GroupBox):

    Title = 'Builder'

    def __init__(self):
        super().__init__(QVBoxLayout)

        self.TFPath = Dir.joinpath('config', 't-finish.pickle')
        self.TFinish = do_pickle(self.TFPath, lambda: [])

        self.PBarLayout = self.create_pbar_layout()
        self.PBars = self.create_pbars()
        self.create_update_button()

    def update(self):
        for pbar in self.PBars:
            pbar.update()

    def create_pbar_layout(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        self.Layout.addLayout(layout)
        return layout

    def create_pbars(self):
        pbars = [VPBar(t) for t in self.TFinish]
        for pbar in pbars:
            self.PBarLayout.addWidget(pbar)
        return pbars

    @staticmethod
    def read_times():
        return [t2ts(t) for t in Elvenar.read_construction_timers()]

    def update_times(self):
        self.TFinish = do_pickle(self.TFPath, self.read_times, redo=True)
        for pbar in self.PBars:
            self.PBarLayout.removeWidget(pbar)
        self.PBars = self.create_pbars()
        self.adjustSize()

    def create_update_button(self):
        self.Layout.addWidget(ResetButton(self.update_times), alignment=CEN)


class VPBar(QProgressBar):

    def __init__(self, t_finish: float):
        super().__init__()

        self.configure()

        self.TFinish = t_finish
        self.Duration = t_finish - time()
        self.Notified = False

    def configure(self):
        self.setOrientation(Qt.Vertical)

    def paintEvent(self, event):
        super().paintEvent(event)
        self.setTextVisible(False)
        p = QPainter(self)
        p.rotate(90)
        p.drawText(self.height() // 2 - 20, -8, self.format())

    def update(self):
        time_left = self.TFinish - time()
        self.setFormat(str(timedelta(seconds=round(time_left))) if time_left > 0 else '')
        self.setValue(round(100 * (1 - time_left / self.Duration)))
        if -5 * 60 < time_left < 0 and not self.Notified:
            send_notification('building finished')
            self.Notified = True

