import sys
from pathlib import Path

from ollama import chat
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class TranslationWorker(QThread):
    translated = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, transcript: str):
        super().__init__()
        self.transcript = transcript

    def run(self):
        try:
            response = chat(
                model="llama3.2",
                messages=[
                    {
                        "role": "system",
                        "content": (
                             "You are a meeting assistant. "
                             "Summarize the provided transcript using "
                            "these sections: Meeting Summary, "
                            "Key Decisions, Action Items, and "
                            "Next Steps. Do not invent details."
                        ),
                    },
                    {"role": "user", "content": self.transcript},
                ],
            )
            result = response.message.content.strip()
            if not result:
                raise ValueError("The model returned an empty translation.")
            self.translated.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


class TranscriptTranslator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.setWindowTitle("Transcript Translator — Llama 3.2")
        self.resize(900, 560)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        tools = QHBoxLayout()
        load_button = QPushButton("Load Transcript (.txt)")
        load_button.clicked.connect(self.load_transcript)
        tools.addWidget(load_button)

        #tools.addWidget(QLabel("Translate to:"))
        #self.language = QComboBox()
        #self.language.addItems([
        #    "English",
        #])
        tools.addStretch()
        layout.addLayout(tools)

        editors = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel("Original transcript"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Paste your meeting transcript here, or load a text file...")
        left.addWidget(self.input_text)
        editors.addLayout(left)

        right = QVBoxLayout()
        right.addWidget(QLabel("Translated transcript"))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        right.addWidget(self.output_text)
        editors.addLayout(right)
        layout.addLayout(editors)

        actions = QHBoxLayout()
        self.translate_button = QPushButton("Translate with Llama 3.2")
        self.translate_button.clicked.connect(self.start_translation)
        actions.addWidget(self.translate_button)

        self.save_button = QPushButton("Save Translation")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_translation)
        actions.addWidget(self.save_button)
        layout.addLayout(actions)

        self.status_label = QLabel("Ready — Ollama must be running locally.")
        layout.addWidget(self.status_label)

    def load_transcript(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select transcript", "", "Text files (*.txt *.md *.srt *.vtt);;All files (*)"
        )
        if not filename:
            return
        try:
            self.input_text.setPlainText(Path(filename).read_text(encoding="utf-8-sig"))
            self.status_label.setText(f"Loaded: {Path(filename).name}")
        except (OSError, UnicodeError) as exc:
            QMessageBox.critical(self, "Cannot open file", str(exc))

    def start_translation(self):
        transcript = self.input_text.toPlainText().strip()
        if not transcript:
            QMessageBox.warning(self, "Missing transcript", "Paste or load a transcript first.")
            return

        self.output_text.clear()
        self.translate_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.status_label.setText("Translating locally with Llama 3.2...")

        self.worker = TranslationWorker(transcript)
        self.worker.translated.connect(self.translation_complete)
        self.worker.failed.connect(self.translation_failed)
        self.worker.finished.connect(self.translation_finished)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def translation_complete(self, result):
        self.output_text.setPlainText(result)
        self.save_button.setEnabled(True)
        self.status_label.setText("Translation complete. You can save it now.")

    def translation_failed(self, message):
        self.status_label.setText("Translation failed.")
        QMessageBox.critical(
            self, "Translation error",
            f"Could not translate the transcript.\n\n{message}\n\n"
            "Check that Ollama is running and llama3.2 has been downloaded.",
        )

    def translation_finished(self):
        self.translate_button.setEnabled(True)
        self.worker = None

    def save_translation(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save translated transcript", "translated_transcript.txt", "Text files (*.txt)"
        )
        if not filename:
            return
        try:
            Path(filename).write_text(self.output_text.toPlainText(), encoding="utf-8")
            self.status_label.setText(f"Saved: {filename}")
        except OSError as exc:
            QMessageBox.critical(self, "Cannot save file", str(exc))

    def closeEvent(self, event):
        if self.worker is not None and self.worker.isRunning():
            QMessageBox.information(self, "Translation running", "Finish translating before closing the window.")
            event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranscriptTranslator()
    window.show()
    sys.exit(app.exec_())
