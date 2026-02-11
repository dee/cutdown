from PyQt6.QtWidgets import QApplication

from ui import MainWindow
from core import ProgressParser


def run():
    app = QApplication([])
    p = ProgressParser()
    mw = MainWindow(p)
    mw.show()
    app.exec()


if __name__ == "__main__":
    run()
