from ui.ui_mainwindow import Ui_MainWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QDialog
import pyperclip


class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.edtOutput.setText("output.mp4")
        self.clipboard_content = ""
        self.ui.pbMain.setValue(0)

        # establish timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer)
        self.timer.setInterval(500)
        self.timer.start()

    def on_timer(self):
        new_text = pyperclip.paste()
        if new_text == self.clipboard_content:
            return
        self.clipboard_content = new_text
        self.ui.edtClipboard.setPlainText(self.clipboard_content)


def run():
    app = QApplication([])
    mw = MainWindow()
    mw.show()
    app.exec()


if __name__ == "__main__":
    run()
