from PyQt5.QtWidgets import QHBoxLayout, QProgressBar

from gui.group_box import GroupBox
from gui.utils import TmpDir, SvgButton, FigDir, QLineEdit
from src.utils import send_notification
from utils.helpers import do_pickle, timedelta, np, time, do, do_nothing, isfloat, isint


def str2time(s: str) -> int:
    t = np.sum(np.array(s.split(':')).astype('i') * [60 ** 2, 60]) if ':' in s else 60 * float(s)
    return round(t)


class Timer(GroupBox):

    Title = 'Timer'
    PicklePath = TmpDir.joinpath('timer.pickle')

    def __init__(self):
        super().__init__(QHBoxLayout)

        self.Duration, self.TFinish = do_pickle(Timer.PicklePath, lambda: (None, None))

        self.PBar = self.create_progress_bar()
        self.TimeEdit = self.create_entry_field()
        self.create_widgets()

        self.Notified = False

    def update(self):
        if self.Duration is not None:
            t_left = self.TFinish - time()
            self.PBar.setValue(round(self.Duration - t_left))
            self.PBar.setFormat(str(timedelta(seconds=round(t_left))) if t_left > 0 else 'Done')
            if -5 * 60 < t_left < 0 and not self.Notified:
                send_notification(f'{timedelta(seconds=self.Duration)} are over')
                self.Notified = True
        else:
            self.PBar.reset()

    def create_progress_bar(self) -> QProgressBar:
        pbar = QProgressBar(self)
        self.Layout.addWidget(pbar)
        if self.Duration is not None:
            pbar.setMaximum(self.Duration)
        return pbar

    def create_entry_field(self):
        te = TimeEdit(length=50, f=self.start)
        self.Layout.addWidget(te)
        return te

    def start(self):
        x = self.TimeEdit.value
        if x is not None:
            self.Duration, self.TFinish = do_pickle(self.PicklePath, lambda: (x, time() + x), redo=True)
            self.PBar.setMaximum(self.Duration)
        self.Notified = False

    def stop(self):
        self.Duration, self.TFinish = do_pickle(self.PicklePath, lambda: (None, None), redo=True)
        self.TimeEdit.setText('')

    def create_widgets(self):
        """start and stop buttons"""
        self.Layout.addWidget(SvgButton(self.start, FigDir.joinpath('start'), size=(20, 20)))
        self.Layout.addWidget(SvgButton(self.stop, FigDir.joinpath('stop'), size=(20, 20)))


class TimeEdit(QLineEdit):

    def __init__(self, txt='', length=None, placeholder='00:00', f=do_nothing):
        super().__init__()
        self.setText(str(txt))
        do(self.setMaximumWidth, length)
        do(self.setPlaceholderText, placeholder)
        self.returnPressed.connect(f)  # noqa

    @property
    def value(self):
        s = self.text()
        return str2time(s) if s else None

    def add(self, x: float):
        s = self.text()
        s = s if s else 0
        if isfloat(x):
            r = float(s) + x
            self.setText('' if r <= 0 else str(round(r)) if isint(r) else f'{r:.1f}')

    def wheelEvent(self, event):
        self.add(1 if event.angleDelta().y() > 0 else -1)
        event.accept()

