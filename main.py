from ui.ui_mainwindow import Ui_MainWindow
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog
import pyperclip


class MainWindow(QDialog):

    can_start = pyqtSignal(bool)
    can_stop = pyqtSignal(bool)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.edtOutput.setText("output.mp4")
        self.ui.pbMain.setValue(0)
        self.ui.btnStart.setDefaultAction(self.ui.actionStart)
        self.ui.btnStop.setDefaultAction(self.ui.actionStop)

        # establish timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer)
        self.timer.setInterval(500)
        self.timer.start()

        # set up actions
        self.ui.actionStart.triggered.connect(self.on_actionStart_triggered)
        self.ui.actionStop.triggered.connect(self.on_actionStop_triggered)

        # other slots
        self.ui.edtClipboard.textChanged.connect(self.on_txtClipboard_changed)
        self.can_start.connect(self.on_can_start)
        self.can_stop.connect(self.on_can_stop)

        # emit status signal
        self.can_start.emit(True)
        self.can_stop.emit(False)

    def on_timer(self):
        new_text = pyperclip.paste()
        if new_text == self.ui.edtClipboard.toPlainText():
            return
        self.ui.edtClipboard.setPlainText(new_text)

    def on_actionStart_triggered(self):
        pass

    def on_actionStop_triggered(self):
        pass

    def on_txtClipboard_changed(self):
        new_text = self.ui.edtClipboard.toPlainText()
        flag = new_text is not None and new_text.endswith(".m3u8")
        self.can_start.emit(flag)

    def on_can_start(self, flag: bool):
        self.ui.actionStart.setEnabled(flag)

    def on_can_stop(self, flag: bool):
        self.ui.actionStop.setEnabled(flag)


def run():
    app = QApplication([])
    mw = MainWindow()
    mw.show()
    app.exec()


if __name__ == "__main__":
    run()
