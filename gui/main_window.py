from sys import exit as ex

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFontDialog, QAction, QApplication

from gui.tools import ToolBox, Elvenar
from gui.motivate import HelpBox
from gui.utils import *
from utils.helpers import Dir


class Gui(QMainWindow):

    Width = 500
    Height = 200
    X = 1597
    Y = 737
    BUTTON_HEIGHT = 50
    Version = 1.0
    Title = f'Elvenar Helper {Version}'
    T_UPDATE = 500

    def __init__(self):
        super(Gui, self).__init__()

        self.Layout = self.create_layout()

        # SUB-LAYOUTS

        self.ToolBox = ToolBox()
        self.Layout.addWidget(self.ToolBox)
        self.HelpBox = HelpBox()
        self.Layout.addWidget(self.HelpBox)
        self.MenuBar = MenuBar(self)

        self.adjustSize()

        self.Timer = self.create_timer()
        self.show()

    def configure(self):
        self.setGeometry(Gui.X, Gui.Y, Gui.Width, Gui.Height)
        self.setWindowTitle(Gui.Title)
        self.setWindowIcon(QIcon(str(Dir.joinpath('figures', 'icoc.png'))))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def create_layout(self) -> QVBoxLayout:
        self.configure()
        layout = QVBoxLayout()
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(layout)
        return layout  # noqa

    @staticmethod
    def get_mouse_pos():
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText('({:1.0f}, {:1.0f})'.format(*Elvenar.Mouse.position()), mode=cb.Clipboard)

    def create_timer(self) -> QTimer:
        t = QTimer()
        t.timeout.connect(self.update)  # noqa
        t.start(Gui.T_UPDATE)
        return t

    def closeEvent(self, event):
        pass
        # self.MenuBar.close_app()

    def update(self):
        self.ToolBox.update()
        self.HelpBox.update()


class MenuBar(object):

    def __init__(self, gui):
        self.Window = gui
        self.Menues = {}
        self.load()

    def load(self):
        self.add_menu('File')
        self.add_menu('Mouse')
        self.add_menu_entry('File', 'Exit', 'Ctrl+Q', close_app, 'Close the Application')
        self.add_menu_entry('File', 'Font', 'Ctrl+F', self.font_choice, 'Open font dialog')
        self.add_menu_entry('Mouse', 'Position', 'Ctrl+M', Gui.get_mouse_pos, 'Open font dialog')

    def add_menu(self, name):
        self.Window.statusBar()
        main_menu = self.Window.menuBar()
        self.Menues[name] = main_menu.addMenu('&{n}'.format(n=name))

    def add_menu_entry(self, menu, name, shortcut, func, tip=''):
        action = QAction('&{n}'.format(n=name), self.Window)
        action.setShortcut(shortcut)
        action.setStatusTip(tip)
        action.triggered.connect(func)  # noqa
        self.Menues[menu].addAction(action)

    def font_choice(self):
        font, valid = QFontDialog.getFont()
        if valid:
            pass


def close_app():
    print('Closing application')
    ex(2)
