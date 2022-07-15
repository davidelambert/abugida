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


def word(n_syl: None | int = None) -> str:
    if n_syl is None:
        n_syl = random.randint(1, 3)

    if n_syl == 0:
        n_syl = random.randint(1, 3)

    if n_syl < 0:
        n_syl = abs(n_syl)

    if n_syl > 3:
        n_syl = n_syl % 3

    text = ''
    i = 0
    while i < n_syl - 1:
        text = text + random.choice(SYLLABLES) + '-'
        i += 1
    text = text + random.choice(SYLLABLES)  # no hyphen after last syllable

    return text


def line(n_syl: None | int = None) -> str:
    if n_syl is None:
        n_syl = random.choice([4, 7])

    if n_syl == 0:
        n_syl = random.choice([4, 7])

    if n_syl < 0:
        n_syl = abs(n_syl)

    if n_syl > 8:
        n_syl = n_syl % 7

    text = ''
    syl_remaining = n_syl

    w1_syl = random.randint(1, 3)
    text = text + word(w1_syl) + '  '
    syl_remaining -= w1_syl

    if syl_remaining > 3:
        w2_syl = random.randint(1, 3)
        text = text + word(w2_syl) + '  '
        syl_remaining -= w2_syl
    elif syl_remaining != 0:
        w2_syl = random.randint(1, syl_remaining)
        text = text + word(w2_syl) + '  '
        syl_remaining -= w2_syl

    if syl_remaining >= 3:
        w3_syl = random.randint(1, 3)
        w3 = word(w3_syl)
        text = text + w3 + '  '
        syl_remaining -= w3_syl
    elif syl_remaining != 0:
        w3 = word(syl_remaining)
        text = text + w3
        syl_remaining -= syl_remaining

    if syl_remaining != 0:
        w4 = word(syl_remaining)
        text = text + w4
        syl_remaining -= syl_remaining

    if syl_remaining != 0:
        raise Exception

    return text


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abugida 2: Vogon Poetry")
        self.setGeometry(50, 100, 1200, 700)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        log_path = Path('./abugida_logs')
        if not log_path.exists():
            log_path.mkdir()
        now = datetime.now().strftime('%Y-%m-%d-%H:%M')
        log_name = 'vogon_poetry_' + now
        self.log_file = log_path/log_name

        self.label = QLabel('')
        lab_font = self.label.font()
        lab_font.setPixelSize(180)
        lab_font.setBold(True)
        lab_font.setFamily('Helvetica Ultra Compressed')
        self.label.setFont(lab_font)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedWidth(1150)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        btn_row = QHBoxLayout()
        layout.addLayout(btn_row)

        self.btn = QPushButton(u'\u21BB')
        self.btn.clicked.connect(self.generate)
        btn_font = self.btn.font()
        btn_font.setPixelSize(120)
        btn_font.setBold(True)
        self.btn.setFont(btn_font)
        self.btn.setFixedWidth(150)
        btn_row.addWidget(self.btn)

    def generate(self):
        this_line = line()
        self.label.setText(this_line)
        with open(self.log_file, 'a') as f:
            f.write(this_line + '\n')


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
