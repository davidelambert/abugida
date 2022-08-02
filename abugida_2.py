import sys
import random
from pathlib import Path
from tempfile import gettempdir

import pySpeakNG
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

HERE = Path(__file__).parent.resolve()
TMP = Path(gettempdir())

VOW = {'A': 'a', 'U': 'u', 'I': 'i:', 'Au': 'aU', 'Ai': 'aI', 'Ui': 'wi:'}
CON = {'B': 'b', 'G': 'g', 'D': 'd'}
SYL_DISP = [c + v.lower() for c in list(CON) for v in list(VOW)]
SYL_PHON = [c + v for c in CON.values() for v in VOW.values()]


def rand_args():
    args = {
        'voice': random.choice(pySpeakNG.VOICES),
        'pitch': random.randint(0, 100),
        'speed': random.randint(30, 200)
    }

    return args


class Word:
    def __init__(self, n_syl: int | None = None) -> None:
        if not n_syl:
            n_syl = random.randint(1, 5)

        draw = random.choices(range(len(SYL_DISP)), k=n_syl)

        self.syl_disp = [SYL_DISP[i] for i in draw]
        self.display = ''.join(self.syl_disp)
        self.text = ''.join(self.syl_disp)

        self.syl = [SYL_PHON[i] for i in draw]
        if len(self.syl) == 1:
            stress = random.choice([True, False])
            if stress:
                self.syl[0] = "'" + self.syl[0]
        elif len(self.syl) > 3:
            stress1, stress2 = random.sample(range(len(self.syl)), k=2)
            self.syl[stress1] = "'" + self.syl[stress1]
            self.syl[stress2] = "," + self.syl[stress2]
        else:
            stress1 = random.choice(range(len(self.syl)))
            self.syl[stress1] = "'" + self.syl[stress1]

        self.phonetic = ''.join(self.syl)

    def __repr__(self) -> str:
        return self.text

    def __str__(self) -> str:
        return self.phonetic


class Line:
    def __init__(self, n_words: None | int = None,
                 n_syl: None | tuple[int] = None) -> None:

        if not n_words and not n_syl:
            n_words = random.randint(1, 5)
            n_syl = [None] * n_words

        if n_words and not n_syl:
            n_syl = [None] * n_words

        if not n_syl and not n_words:
            n_words = len(n_syl)

        self.objects = [Word(n_syl=n_syl[w]) for w in range(n_words)]
        self.words = [str(obj) for obj in self.objects]
        self.phonetic = ' '.join(self.words)
        self.display = ' '.join([obj.display for obj in self.objects])
        self.text = self.display.replace('-', '')

    def __repr__(self) -> str:
        return self.text

    def __str__(self) -> str:
        return self.phonetic


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
        self.sound_file = None

        # LINE DISPLAY ===================
        self.line = Line()
        self.label = QLabel(self.line.display)
        lab_font = self.label.font()
        lab_font.setPixelSize(180)
        lab_font.setBold(True)
        lab_font.setFamily('Helvetica Extra Compressed')
        lab_font.setWordSpacing(40)
        self.label.setFont(lab_font)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # BUTTONS ================================
        btn_maingrp = QHBoxLayout()
        btn_maingrp.setAlignment(Qt.AlignHCenter)
        btn_maingrp.setSpacing(50)
        layout.addLayout(btn_maingrp)

        self.btn_generate = QPushButton(u'\u21BB')
        self.btn_generate.clicked.connect(self.new_line)
        btn_font = self.btn_generate.font()
        btn_font.setPixelSize(40)
        self.btn_generate.setFont(btn_font)
        self.btn_generate.setFixedSize(BSIZE, BSIZE)
        btn_maingrp.addWidget(self.btn_generate)

        self.btn_play = QPushButton(u'\u25B6')
        self.btn_play.clicked.connect(self.speak)
        self.btn_play.setFont(btn_font)
        self.btn_play.setFixedSize(BSIZE, BSIZE)
        btn_maingrp.addWidget(self.btn_play)

        self.btn_log = QPushButton(u'\u25CF')
        self.btn_log.setCheckable(True)
        self.btn_log.clicked.connect(self.toggle_log)
        self.btn_log.setFont(btn_font)
        self.btn_log.setFixedSize(BSIZE, BSIZE)
        btn_maingrp.addWidget(self.btn_log)

    def new_line(self):
        self.line = Line()
        self.label.setText(self.line.display)
        if self.log_on:
            with open(self.log_file, 'a') as f:
                f.write(self.line.text + '\n')

    def speak(self):
        pySpeakNG.speak(f"[[{self.line}]]", **rand_args())

    def toggle_log(self, checked):
        if not self.log_file:
            self.log_file = QFileDialog.getSaveFileName(
                self, directory=str(Path.home()))[0]
        self.log_on = checked


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
