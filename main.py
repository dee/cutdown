from ui.ui_mainwindow import Ui_MainWindow
from PyQt5.QtCore import QTimer, pyqtSignal, QProcess
from PyQt5.QtWidgets import QApplication, QDialog
from parser import ProgressParser
import pyperclip
import subprocess
import os


class MainWindow(QDialog):

    can_start = pyqtSignal(bool)
    can_stop = pyqtSignal(bool)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.process = None

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Videosaver")
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
        self.ui.actionStart.triggered.connect(self.on_action_start)
        self.ui.actionStop.triggered.connect(self.on_action_stop)

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

    def build_cmd_line(self) -> str:
        full_output_path = os.path.join(os.getcwd(), self.ui.edtOutput.text())
        print(f"Using output path: {full_output_path}")
        manifest = self.ui.edtClipboard.toPlainText()
        return [manifest, "-r", "200K", "-o"+full_output_path]

    def on_action_start(self):
        print("Start button pressed")
        self.ui.edtLog.clear()

        if self.process is not None:
            self.process.deleteLater()
            self.process = None

        self.process = QProcess(self)
        self.process.setProgram("yt-dlp")
        self.process.setArguments(self.build_cmd_line())
        self.process.readyReadStandardOutput.connect(self.on_readyread_stdout)
        self.process.readyReadStandardError.connect(self.on_readyread_stderr)
        self.process.stateChanged.connect(self.on_process_state_changed)
        self.process.finished.connect(self.on_process_finished)
        self.process.start()
        self.can_start.emit(False)
        self.can_stop.emit(True)

    def on_action_stop(self):
        print("Stop button pressed")
        self.process.terminate()

    def on_txtClipboard_changed(self):
        new_text = self.ui.edtClipboard.toPlainText()
        flag = new_text is not None and new_text.find("m3u8") != -1
        self.can_start.emit(flag)

    def on_can_start(self, flag: bool):
        self.ui.actionStart.setEnabled(flag)

    def on_can_stop(self, flag: bool):
        self.ui.actionStop.setEnabled(flag)

    def on_readyread_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8").rstrip()
        # print(f"OUT: {stdout}")
        self.ui.edtLog.appendPlainText(stdout)
        p = ProgressParser()
        (progress, eta) = p.parse(stdout)
        print(f"Parsed: {progress}")
        if progress is not None:
            self.ui.pbMain.setValue(progress)
        if eta is not None:
            # TODO: set text on a progress bar?
            pass

    def on_readyread_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8").rstrip()
        print(f"ERR: {stderr}")
        self.ui.edtLog.appendPlainText(stderr)

    def on_process_state_changed(self, state):
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states.get(state, 'Unknown')
        print(f"State changed: {state_name}")

    def on_process_finished(self):
        print(f"Process finished!")
        self.can_start.emit(True)
        self.can_stop.emit(False)

        # 
        # [download]   2.8% of ~ 965.47MiB at  184.83KiB/s ETA 01:54:52 (frag 0/32)
        # [download]   2.8% of ~ 971.72MiB at  189.37KiB/s ETA 01:51:26 (frag 0/32)


def run():
    app = QApplication([])
    mw = MainWindow()
    mw.show()
    app.exec()


if __name__ == "__main__":
    run()
