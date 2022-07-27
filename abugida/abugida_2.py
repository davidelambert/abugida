import sys
import random
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *


HERE = Path(__file__).parent.resolve()

VOWELS = ('A', 'U', 'I', 'Ai', 'Au')
CONSONANTS = ('B', 'G', 'D')
SYLLABLES = [c + v.lower() for c in CONSONANTS for v in VOWELS] + list(VOWELS)

MAX_SYL = 4


def word(n_syl: None | int = None) -> str:
    if n_syl is None:
        n_syl = random.randint(1, MAX_SYL)

    if n_syl == 0:
        n_syl = random.randint(1, MAX_SYL)

    if n_syl < 0:
        n_syl = abs(n_syl)

    if n_syl > MAX_SYL:
        n_syl = n_syl % MAX_SYL

    text = ''
    i = 0
    while i < n_syl - 1:  # all but last syllable
        text = text + random.choice(SYLLABLES) + '-'
        i += 1
    text = text + random.choice(SYLLABLES)  # no hyphen after last syllable

    return text


def line() -> str:
    max_length = 30
    n_words = random.randint(3, 5)
    text = ''

    i = 0
    while i < n_words:
        text += word()
        if len(text) < max_length:
            text += ' '
        i += 1

    while len(text) > max_length:
        text = text[:text.rfind('-')]

    return text


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abugida 2: Vogon Poetry")
        self.showMaximized()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        BSIZE = 80
        self.log_on = False
        self.log_file = None

        # LINE DISPLAY ===================
        init_line = line()
        self.label = QLabel(init_line)
        lab_font = self.label.font()
        lab_font.setPixelSize(200)
        lab_font.setBold(True)
        lab_font.setFamily('Helvetica Ultra Compressed')
        lab_font.setWordSpacing(40)
        self.label.setFont(lab_font)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # GENERATE & LOG BUTTONS ================================
        btn_maingrp = QHBoxLayout()
        btn_maingrp.setAlignment(Qt.AlignHCenter)
        btn_maingrp.setSpacing(50)
        layout.addLayout(btn_maingrp)

        self.btn_generate = QPushButton(u'\u21BB')  # cwise open circle arrow ↻
        self.btn_generate.clicked.connect(self.generate)
        btn_font = self.btn_generate.font()
        btn_font.setPixelSize(40)
        self.btn_generate.setFont(btn_font)
        self.btn_generate.setFixedSize(BSIZE, BSIZE)
        btn_maingrp.addWidget(self.btn_generate)

        self.btn_log = QPushButton(u'\u25CF')
        self.btn_log.setCheckable(True)
        self.btn_log.clicked.connect(self.toggle_log)
        self.btn_log.setFont(btn_font)
        self.btn_log.setFixedSize(BSIZE, BSIZE)
        btn_maingrp.addWidget(self.btn_log)

    def generate(self):
        this_line = line()
        self.label.setText(this_line)
        if self.log_on:
            with open(self.log_file, 'a') as f:
                f.write(this_line.replace('-', '') + '\n')

    def toggle_log(self, checked):
        if not self.log_file:
            self.log_file = QFileDialog.getSaveFileName(
                self, directory=str(Path.home()))[0]
        self.log_on = checked


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
