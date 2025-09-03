import pyperclip
import subprocess
import os
from PyQt5.QtWidgets import QApplication

from ui import MainWindow
from parser import ProgressParser


def run():
    app = QApplication([])
    p = ProgressParser()
    mw = MainWindow(p)
    mw.show()
    app.exec()


if __name__ == "__main__":
    run()