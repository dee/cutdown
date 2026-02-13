from PyQt6.QtCore import pyqtSignal, QProcess, Qt
from PyQt6.QtGui import QClipboard
from PyQt6.QtWidgets import QApplication, QDialog
from .ui_mainwindow import Ui_MainWindow
import os
from loguru import logger


class MainWindow(QDialog):
    can_start = pyqtSignal(bool)
    can_stop = pyqtSignal(bool)

    def __init__(self, parser):
        super(MainWindow, self).__init__()

        self.parser = parser
        self.process = None

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("cutdown")
        self.ui.edtOutput.setText("output.mp4")
        self.ui.pbMain.setValue(0)
        self.ui.btnStart.setDefaultAction(self.ui.actionStart)
        self.ui.btnStop.setDefaultAction(self.ui.actionStop)
        self.ui.spnValue.setValue(200)
        self.ui.rbKbit.setDown(True)
        self.ui.chkUnlimited.setCheckState(Qt.CheckState.Unchecked)

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

        # connect to a clipboard
        self.last_clipboard_text = ""
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_dataChanged)
        logger.debug(f"Started, work directory: {os.getcwd()}")

    def build_cmd_line(self) -> []:
        result = []
        full_output_path = os.path.join(os.getcwd(), self.ui.edtOutput.text())
        manifest = self.ui.edtClipboard.toPlainText()
        result.append(manifest)
        if self.ui.chkUnlimited.checkState() == Qt.CheckState.Unchecked:
            result.append("-r")
            unit = "K"
            if self.ui.rbMbit.isDown():
                unit = "M"
            result.append(f"{self.ui.spnValue.value()}{unit}")
        result.append("-o"+full_output_path)
        logger.debug(f"Command line: {result}")
        return result

    def on_action_start(self):
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
        self.process.terminate()

    def on_clipboard_dataChanged(self):
        try:
            current_text = self.clipboard.text(QClipboard.Mode.Clipboard)
            if current_text and current_text != self.last_clipboard_text:
                self.last_clipboard_text = current_text
                self.ui.edtClipboard.setPlainText(current_text)
                logger.debug(f"Clipboard text {current_text}")
        except Exception:
            logger.exception("Clipboard error")

    def on_txtClipboard_changed(self):
        new_text = self.ui.edtClipboard.toPlainText()
        
        if new_text is None:
            return

        manifest = new_text.find("m3u8") != -1
        # TODO: regexp
        youtube = new_text.startswith("https://www.youtube.com/watch?v=")
        self.can_start.emit(manifest or youtube)

    def on_can_start(self, flag: bool):
        self.ui.actionStart.setEnabled(flag)

    def on_can_stop(self, flag: bool):
        self.ui.actionStop.setEnabled(flag)

    def on_readyread_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8").rstrip()
        (progress, eta) = self.parser.parse(stdout)

        if progress is None and eta is None:
            self.ui.edtLog.appendPlainText(stdout)
        if progress is not None:
            self.ui.pbMain.setValue(progress)
        if eta is not None:
            self.ui.pbMain.setFormat(eta)
        else:
            self.ui.pbMain.setFormat("Unknown")

    def on_readyread_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8").rstrip()
        self.ui.edtLog.appendPlainText(stderr)

    def on_process_state_changed(self, state):
        states = {
            QProcess.ProcessState.NotRunning: "Not running",
            QProcess.ProcessState.Starting: "Starting",
            QProcess.ProcessState.Running: "Running",
        }
        state_name = states.get(state, "Unknown")
        logger.debug(f"Process state changed: {state_name}")

    def on_process_finished(self):
        logger.debug("Process finished!")
        self.can_start.emit(True)
        self.can_stop.emit(False)

    def on_chkUnlimited_checkStateChanged(self):
        check_state = self.ui.chkUnlimited.checkState()
        flag = check_state == Qt.CheckState.Unchecked
        self.ui.spnValue.setEnabled(flag)
        self.ui.rbKbit.setEnabled(flag)
        self.ui.rbMbit.setEnabled(flag)