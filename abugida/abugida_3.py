import sys
import random
from datetime import datetime
from pathlib import Path
from string import ascii_uppercase

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

HERE = Path(__file__).parent.resolve()

LETTERS = set(ascii_uppercase)
drop_cons = ['Q', 'C', 'X']
for c in drop_cons:
    LETTERS.remove(c)

SINGLE_VOWELS = set('AEIOU')
DIPHTONGS = {'Ai', 'Au', 'Oi', }
VOWELS = SINGLE_VOWELS.union(DIPHTONGS)

DIGRAPHS = {'Ch', 'Sh', 'Th', "Zh"}
CONSONANTS = LETTERS.difference(SINGLE_VOWELS).union(DIGRAPHS)


def word(vowels: list[str] = ['A', 'U', 'I'], consonants: list[str]
         = ['B', 'G', 'D'], n_syl: int | None = None) -> str:
    """Generate a word of one to three syllables, which are themselves composed
    of all possible consonant-vowel and single-vowel permutations.

    Args:
        vowels (list[str], optional): A list of vowels used to make syllables.
            Accepts single vowels, including y, and all non-repetitive
            diphthongs of single vowels, (not 'aa', 'ee'). Defaults to
            ['A', 'U', 'I'].
        consonants (list[str], optional): A list of consonants used to make
            syllables. Accepts single consonants plus: 'ch', 'sh', 'th'.
            Defaults to  ['B', 'G', 'D'].
        n_syl (int | None, optional): The integer number of syllables in
            the word, from one to three. Negative numbers are interpreted as
            their absolute values. Numbers greater than 3 are interpreted
            modulo 3. The default, None, or 0, return a word with a random
            number of either one, two, or three syllables.

    Returns:
        str: A word of `n_syl` syllables, composed of `consonants` and `vowels`
        in CV or V permutations, with syllables separated by hyphens.
    """

    max_syl = 4

    vowels = [v[:2] for v in vowels]
    vowels = [v.capitalize() for v in vowels]
    vowels = list(VOWELS.intersection(vowels))
    if not vowels:
        vowels = ['A', 'U', 'I']

    for c in consonants:
        if c.capitalize() not in CONSONANTS:
            consonants.remove(c)
        c = c.capitalize()
    if not consonants:
        consonants = ['B', 'G', 'D']

    cv_syl = [c + v.lower() for c in consonants for v in vowels]
    all_syl = cv_syl + vowels

    if n_syl is None:
        n_syl = random.randint(1, max_syl)

    if n_syl == 0:
        n_syl = random.randint(1, max_syl)

    if n_syl < 0:
        n_syl = abs(n_syl)

    if n_syl > max_syl:
        n_syl = n_syl % max_syl

    text = ''
    i = 0
    while i < n_syl - 1:  # all but last syllable
        text += random.choice(all_syl)
        text += '-'
        i += 1
    text += random.choice(all_syl)  # last syllable: no hyphen

    return text


def line(vowels: list[str] | None = None, consonants: list[str] | None = None,
         n_syl: int | None = None) -> str:
    """Generate a line of 3-5 words, of up to 30 characters.

    Returns:
        str: A line of words up to 30 characters long, contructed from
        available CV and/or V syllables.
    """

    max_length = 30

    n_words = random.randint(3, 5)

    text = ''
    i = 0
    while i < n_words:
        text += word(vowels=vowels, consonants=consonants, n_syl=n_syl)
        if len(text) < max_length:
            text += ' '
        i += 1

    while len(text) > max_length:
        text = text[:text.rfind('-')]

    return text


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "Abugida 3: Abugida Babalu/Einstürzende Zikkuraten")
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
        log_name = 'babalu_' + now
        if Path(log_path/log_name).exists():
            log_name += datetime.now().strftime(':%S')
        self.log_file = log_path/log_name

        # LETTER SELECTION ================================
        select = QHBoxLayout()
        select.setContentsMargins(50, 0, 50, 0)
        layout.addLayout(select)

        self.vow_active = random.sample(list(VOWELS), 3)
        self.con_active = random.sample(list(CONSONANTS), 3)

        # VOWELS =============================================
        vgrid = QGridLayout()
        vgrid.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        vgrid.setContentsMargins(20, 20, 20, 20)
        vgrid.setSpacing(50)

        vdim = (2, 4)
        vmat = [(row, col) for row in range(vdim[0]) for col in range(vdim[1])]
        vdict = dict(zip(sorted(VOWELS), vmat))

        self.vow_cb = []
        for v, loc in vdict.items():
            exec("self.cb_{} = QCheckBox('{}')".format(v, v))
            if v in self.vow_active:
                exec("self.cb_{}.setCheckState(Qt.Checked)".format(v))
            exec("self.cb_{}.stateChanged.connect(self.update_vow)".format(v))
            exec("vgrid.addWidget(self.cb_{}, {}, {})"
                 .format(v, loc[0], loc[1]))
            exec("self.vow_cb.append(self.cb_{})".format(v))

        vgroup = QGroupBox('Vowels/Diphthongs')
        vgroup.setLayout(vgrid)
        vgroup.setFixedSize(400, 400)
        select.addWidget(vgroup, alignment=Qt.AlignTop)

        # CONSONANTS ===============================================
        cgrid = QGridLayout()
        cgrid.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        cgrid.setContentsMargins(20, 20, 20, 20)
        cgrid.setSpacing(50)

        cdim = (4, 6)
        cmat = [(row, col) for row in range(cdim[0]) for col in range(cdim[1])]
        cdict = dict(zip(sorted(CONSONANTS), cmat))

        self.con_cb = []
        for c, loc in cdict.items():
            exec("self.cb_{} = QCheckBox('{}')".format(c, c))
            if c in self.con_active:
                exec("self.cb_{}.setCheckState(Qt.Checked)".format(c))
            exec("self.cb_{}.stateChanged.connect(self.update_cons)".format(c))
            exec("cgrid.addWidget(self.cb_{}, {}, {})"
                 .format(c, loc[0], loc[1]))
            exec("self.con_cb.append(self.cb_{})".format(c))

        cgroup = QGroupBox('Consonants/Digraphs')
        cgroup.setLayout(cgrid)
        cgroup.setFixedSize(600, 400)
        select.addWidget(cgroup, alignment=Qt.AlignTop)

        # CONTROLS ============================================
        btn_grid = QVBoxLayout()
        btn_grid.setAlignment(Qt.AlignCenter)
        btn_grid.setContentsMargins(20, 20, 20, 20)
        btn_grid.setSpacing(25)

        btn_all = QPushButton(u'\u221E')  # infinity ∞
        btn_font = btn_all.font()
        btn_font.setPixelSize(40)
        btn_all.setFont(btn_font)
        btn_all.clicked.connect(self.select_all)
        btn_all.setFixedSize(BSIZE, BSIZE)
        btn_grid.addWidget(btn_all)

        btn_none = QPushButton(u'\u2300')  # diameter ⌀, for null
        btn_none.setFont(btn_font)
        btn_none.clicked.connect(self.select_none)
        btn_none.setFixedSize(BSIZE, BSIZE)
        btn_grid.addWidget(btn_none)

        btn_random = QPushButton(u'\u2684')  # die face-5 ⚄
        btn_random.setFont(btn_font)
        btn_random.clicked.connect(self.select_random)
        btn_random.setFixedSize(BSIZE, BSIZE)
        btn_grid.addWidget(btn_random)

        btn_ctrlgrp = QGroupBox('Controls')
        btn_ctrlgrp.setLayout(btn_grid)
        btn_ctrlgrp.setFixedSize(200, 400)
        select.addWidget(btn_ctrlgrp, alignment=Qt.AlignTop)

        # LINE DISPLAY ============================================
        init_line = line(vowels=self.vow_active, consonants=self.con_active)
        self.label = QLabel(init_line)
        lab_font = self.label.font()
        lab_font.setPixelSize(200)
        lab_font.setBold(True)
        lab_font.setFamily('Helvetica Ultra Compressed')
        lab_font.setWordSpacing(40)
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
        this_line = line(vowels=self.vow_active, consonants=self.con_active)
        self.label.setText(this_line)
        if self.log_on:
            with open(self.log_file, 'a') as f:
                f.write(this_line.replace('-', '') + '\n')

    def toggle_log(self, checked):
        self.log_on = checked

    def update_vow(self):
        self.vow_active.clear()
        for cb in self.vow_cb:
            if cb.isChecked():
                self.vow_active.append(cb.text())

    def update_cons(self):
        self.con_active.clear()
        for cb in self.con_cb:
            if cb.isChecked():
                self.con_active.append(cb.text())

    def select_all(self):
        for vow in VOWELS:
            exec("self.cb_{}.setCheckState(Qt.Checked)".format(vow))
        for con in CONSONANTS:
            exec("self.cb_{}.setCheckState(Qt.Checked)".format(con))

    def select_none(self):
        for vow in VOWELS:
            exec("self.cb_{}.setCheckState(Qt.Unchecked)".format(vow))
        for con in CONSONANTS:
            exec("self.cb_{}.setCheckState(Qt.Unchecked)".format(con))

    def select_random(self):
        self.select_none()
        vsamp = random.sample(list(VOWELS), 3)
        for vow in vsamp:
            exec("self.cb_{}.setCheckState(Qt.Checked)".format(vow))
        csamp = random.sample(list(CONSONANTS), 3)
        for con in csamp:
            exec("self.cb_{}.setCheckState(Qt.Checked)".format(con))


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
