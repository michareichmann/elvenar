#!/usr/bin/env python

from argparse import ArgumentParser
import os
import signal
import sys


parser = ArgumentParser()
parser.add_argument('--gui', '-g', action='store_true')
args = parser.parse_args()

os.system('/bin/bash -c "source /home/micha/.bashrc"')  # required for the launcher

if args.gui:
    from gui.main_window import *
    from PyQt5.QtWidgets import QApplication
    from warnings import filterwarnings
    import qdarkstyle

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication([Gui.Title])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    filterwarnings('ignore')

    g = Gui()

    sys.exit(app.exec_())

else:
    from src.elvenar import Elvenar
    from PyQt5.QtWidgets import QApplication
    from gui.utils import *
    app = QApplication(['Test'])
