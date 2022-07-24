import sys
import random
from datetime import datetime
from pathlib import Path
from string import ascii_uppercase

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

HERE = Path(__file__).parent.resolve()
MAX_SYL = 4

ATUP = (u'\u1403', u'\u1405', u'\u1401', u'\u140A')
ASTR = ''.join([a for a in ATUP])
VTUP = (u'\u1431', u'\u1433', u'\u142F', u'\u1438')
VSTR = ''.join([v for v in VTUP])
UTUP = (u'\u144E', u'\u1450', u'\u144C', u'\u1455')
USTR = ''.join(u for u in UTUP)
NORTH = [a for a in ATUP] + [v for v in VTUP] + [u for u in UTUP]

PTUP = (u'\u146B', u'\u146D', u'\u1472', u'\u146F')
PSTR = ''.join(p for p in PTUP)
JTUP = (u'\u1489', u'\u148B', u'\u1490', u'\u148D')
JSTR = ''.join(j for j in JTUP)
LTUP = (u'\u14A3', u'\u14A5', u'\u14AA', u'\u14A7')
LSTR = ''.join(el for el in LTUP)
NORTHWEST = [p for p in PTUP] + [j for j in JTUP] + [el for el in LTUP]

ALL = NORTH + NORTHWEST


def word() -> str:
    n_syl = random.randint(1, MAX_SYL)

    text = ''
    i = 0
    while i < n_syl:
        text = text + random.choice(ALL)
        i += 1

    return text


def line() -> str:
    max_length = 14
    n_words = random.randint(3, 5)
    text = ''

    i = 0
    while i < n_words:
        text += word()
        if len(text) < max_length:
            text += ' '
        i += 1

    while len(text) > max_length:
        text = text[:text.rfind(' ')]

    return text


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abugida 4: Aborugida/Eye Exam")
        self.showMaximized()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        BSIZE = 80

        # LOG SETUP =================================
        self.log_on = False
        log_path = HERE/'abugida_logs'
        if not log_path.exists():
            log_path.mkdir()
        now = datetime.now().strftime('%Y-%m-%d-%H:%M')
        log_name = 'exam_' + now
        if Path(log_path/log_name).exists():
            log_name += datetime.now().strftime(':%S')
        self.log_file = log_path/log_name

        # LETTER SELECTION ================================
        select = QHBoxLayout()
        select.setContentsMargins(50, 0, 50, 0)
        layout.addLayout(select)

        tups = [el + 'TUP' for el in ['A', 'V', 'U', 'P', 'J', 'L']]
        self.active = random.sample(['A', 'V', 'U', 'P', 'J', 'L'], 3)

        # NORTH SYMBOLS =============================================
        n_grid = QVBoxLayout()
        n_grid.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        n_grid.setContentsMargins(20, 20, 20, 20)
        n_grid.setSpacing(50)

        self.n_cb = []
        for grp in ['A', 'V', 'U']:
            exec('self.cb_{} = QCheckBox("{}")'
                 .format(grp, eval(grp + 'STR')))
            if grp in self.active:
                exec('self.cb_{}.setCheckState(Qt.Checked)'.format(grp))
            exec('self.cb_{}.stateChanged.connect(self.update_groups)'
                 .format(grp))
            exec('n_grid.addWidget(self.cb_{})'.format(grp))
            exec('self.n_cb.append(self.cb_{})'.format(grp))

        n_group = QGroupBox('N-E-S-W Characters')
        n_group.setLayout(n_grid)
        n_group.setFixedSize(400, 400)
        select.addWidget(n_group, alignment=Qt.AlignTop)

        # NORTHWEST SYMBOLS =============================================
        nw_grid = QVBoxLayout()
        nw_grid.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        nw_grid.setContentsMargins(20, 20, 20, 20)
        nw_grid.setSpacing(50)

        self.nw_cb = []
        for grp in ['P', 'J', 'L']:
            exec('self.cb_{} = QCheckBox("{}")'
                 .format(grp, eval(grp + 'STR')))
            if grp in self.active:
                exec('self.cb_{}.setCheckState(Qt.Checked)'.format(grp))
            exec('self.cb_{}.stateChanged.connect(self.update_groups)'
                 .format(grp))
            exec('nw_grid.addWidget(self.cb_{})'.format(grp))
            exec('self.nw_cb.append(self.cb_{})'.format(grp))

        nw_group = QGroupBox('NW-NE-SE-SW Characters')
        nw_group.setLayout(nw_grid)
        nw_group.setFixedSize(400, 400)
        select.addWidget(nw_group, alignment=Qt.AlignTop)

        # LINE DISPLAY ============================================
        init_line = line()
        self.label = QLabel(init_line)
        lab_font = self.label.font()
        lab_font.setPixelSize(150)
        lab_font.setBold(True)
        lab_font.setFamily('Ubuntu Mono')
        self.label.setFont(lab_font)
        self.label.setAlignment(Qt.AlignHCenter)
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

        self.btn_log = QPushButton(u'\u33D2')  # log symbol ㏒
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
        self.log_on = checked

    def update_groups(self):
        self.active.clear()
        for cb in self.vow_cb:
            if cb.isChecked():
                self.active.append(cb.text())


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
