import sys
import random
from pathlib import Path

from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtGui
from PyQt5.QtWidgets import *

HERE = Path(__file__).parent.resolve()
MAX_SYL = 4

A = (u'\u1403', u'\u1405', u'\u1401', u'\u140A')
V = (u'\u1431', u'\u1433', u'\u142F', u'\u1438')
U = (u'\u144E', u'\u1450', u'\u144C', u'\u1455')
CARDINAL = [a for a in A] + [v for v in V] + [u for u in U]

P = (u'\u146B', u'\u146D', u'\u1472', u'\u146F')
J = (u'\u1489', u'\u148B', u'\u1490', u'\u148D')
L = (u'\u14A3', u'\u14A5', u'\u14AA', u'\u14A7')
ORDINAL = [p for p in P] + [j for j in J] + [el for el in L]

ALL_CHAR = CARDINAL + ORDINAL
KEYS = ['A', 'V', 'U', 'P', 'J', 'L']
DICT = dict(zip(KEYS, [eval(k) for k in KEYS]))


def word(letters: list[str] = ['A', 'V', 'U']) -> str:
    n_syl = random.randint(1, MAX_SYL)
    choices = [char for grp in [eval(el) for el in letters] for char in grp]

    text = ''
    i = 0
    while i < n_syl:
        text = text + random.choice(choices)
        i += 1

    return text


def line(letters: list[str]) -> str:
    max_length = 14
    n_words = random.randint(3, 5)
    text = ''

    i = 0
    while i < n_words:
        text += word(letters=letters)
        if len(text) < max_length:
            text += ' '
        i += 1

    while len(text) > max_length:
        text = text[:text.rfind(' ')]

    return text


class ShapeCB(QCheckBox):
    def __init__(self, key: str):
        super().__init__()
        self.key = key


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abugida 4: Swampy Cree/Eye Exam")
        self.showMaximized()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        BSIZE = 80
        self.log_on = False
        self.log_file = None

        # LETTER SELECTION ================================
        select = QHBoxLayout()
        select.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        select.setContentsMargins(50, 0, 50, 0)
        select.setSpacing(100)
        layout.addLayout(select)

        self.active = random.sample(KEYS, 3)

        # CARDINALS =============================================
        card_grid = QHBoxLayout()
        card_grid.setAlignment(Qt.AlignCenter)
        card_grid.setContentsMargins(20, 20, 20, 20)
        card_grid.setSpacing(50)

        card_icon = QtGui.QPixmap(str(HERE/'img/card_icon.svg'))
        card_key = QLabel()
        card_key.setPixmap(card_icon)
        card_grid.addWidget(card_key)

        self.all_cb = []
        for g in ['A', 'V', 'U']:
            exec('{}_icon = QtGui.QIcon(str(Path(HERE/"img/{}.svg")))'
                 .format(g, g))
            exec('self.cb_{} = ShapeCB(key="{}")'.format(g, g))
            exec('self.cb_{}.setIcon({}_icon)'.format(g, g))
            exec('self.cb_{}.setIconSize(QSize(64, 64))'.format(g))
            if g in self.active:
                exec('self.cb_{}.setCheckState(Qt.Checked)'.format(g))
            exec('self.cb_{}.stateChanged.connect(self.update)'.format(g))
            exec('card_grid.addWidget(self.cb_{})'.format(g))
            exec('self.all_cb.append(self.cb_{})'.format(g))

        card_group = QGroupBox()
        card_group.setLayout(card_grid)
        select.addWidget(card_group)

        # RANDOM BUTTON ====================================
        btn_random = QPushButton(u'\u2684')
        btn_random.clicked.connect(self.randomize)
        btn_font = btn_random.font()
        btn_font.setPixelSize(40)
        btn_random.setFont(btn_font)
        btn_random.setFixedSize(BSIZE, BSIZE)
        select.addWidget(btn_random)

        # ORDINALS =============================================
        ord_grid = QHBoxLayout()
        ord_grid.setAlignment(Qt.AlignHCenter)
        ord_grid.setContentsMargins(20, 20, 20, 20)
        ord_grid.setSpacing(50)

        ord_icon = QtGui.QPixmap(str(HERE/'img/ord_icon.svg'))
        ord_key = QLabel('')
        ord_key.setPixmap(ord_icon)
        ord_grid.addWidget(ord_key)

        for g in ['P', 'J', 'L']:
            exec('{}_icon = QtGui.QIcon(str(Path(HERE/"img/{}.svg")))'
                 .format(g, g))
            exec('self.cb_{} = ShapeCB(key="{}")'.format(g, g))
            exec('self.cb_{}.setIcon({}_icon)'.format(g, g))
            exec('self.cb_{}.setIconSize(QSize(64, 64))'.format(g))
            if g in self.active:
                exec('self.cb_{}.setCheckState(Qt.Checked)'.format(g))
            exec('self.cb_{}.stateChanged.connect(self.update)'.format(g))
            exec('ord_grid.addWidget(self.cb_{})'.format(g))
            exec('self.all_cb.append(self.cb_{})'.format(g))

        ord_group = QGroupBox()
        ord_group.setLayout(ord_grid)
        select.addWidget(ord_group)

        # LINE DISPLAY ============================================
        init_line = line(letters=self.active)
        self.label = QLabel(init_line)
        lab_font = self.label.font()
        lab_font.setPixelSize(150)
        lab_font.setBold(True)
        lab_font.setFamily('Ubuntu Mono')
        self.label.setFont(lab_font)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # GENERATE & LOG BUTTONS ================================
        btn_maingrp = QHBoxLayout()
        btn_maingrp.setAlignment(Qt.AlignHCenter)
        btn_maingrp.setSpacing(50)
        layout.addLayout(btn_maingrp)

        self.btn_generate = QPushButton(u'\u21BB')  # cwise open circle arrow ↻
        self.btn_generate.clicked.connect(self.generate)
        self.btn_generate.setFont(btn_font)
        self.btn_generate.setFixedSize(BSIZE, BSIZE)
        btn_maingrp.addWidget(self.btn_generate)

        self.btn_log = QPushButton(u'\u25CF')  # black circle ● (for record)
        self.btn_log.setCheckable(True)
        self.btn_log.clicked.connect(self.toggle_log)
        self.btn_log.setFont(btn_font)
        self.btn_log.setFixedSize(BSIZE, BSIZE)
        btn_maingrp.addWidget(self.btn_log)

    def generate(self):
        if not self.active:
            self.randomize()
        this_line = line(self.active)
        self.label.setText(this_line)
        if self.log_on:
            with open(self.log_file, 'a') as f:
                f.write(this_line + '\n')

    def randomize(self):
        sample = random.sample(KEYS, 3)
        for key in KEYS:
            exec('self.cb_{}.setCheckState(Qt.Unchecked)'.format(key))
            if key in sample:
                exec('self.cb_{}.setCheckState(Qt.Checked)'.format(key))

    def toggle_log(self, checked):
        if not self.log_file:
            self.log_file = QFileDialog.getSaveFileName(
                self, directory=str(Path.home()))[0]
        self.log_on = checked

    def update(self):
        self.active.clear()
        for cb in self.all_cb:
            if cb.isChecked():
                self.active.append(cb.key)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
