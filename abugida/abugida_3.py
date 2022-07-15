import sys
import random
from datetime import datetime
from pathlib import Path
from string import ascii_uppercase
from itertools import permutations
import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *


LETTERS = set(ascii_uppercase.replace('Q', ''))
SINGLE_VOWELS = set('AEIOUY')
CONSONANTS = LETTERS.difference(SINGLE_VOWELS).union({'Ch', 'Sh', 'Th'})
DIPHTONGS = {''.join(t).capitalize() for t in permutations(SINGLE_VOWELS, 2)}
VOWELS = SINGLE_VOWELS.union(DIPHTONGS)


def word(vowels: list[str] = ['A', 'U', 'I', 'Ai', 'Au'], consonants: list[str]
         = ['B', 'G', 'D'], n_syl: int | None = None) -> str:
    """Generate a word of one to three syllables, which are themselves composed
    of all possible consonant-vowel and single-vowel permutations.

    Args:
        vowels (list[str], optional): A list of vowels used to make syllables.
            Accepts single vowels, including y, and all non-repetitive
            diphthongs of single vowels, (not 'aa', 'ee'). Defaults to
            ['A', 'U', 'I', 'Ai', 'Au'].
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

    vowels = [v[:2] for v in vowels if len(v) > 2]
    vowels = [v.capitalize() for v in vowels]
    vowels = list(VOWELS.intersection(vowels))
    if not vowels:
        vowels = ['A', 'U', 'I', 'Ai', 'Au']

    for c in consonants:
        if c.lower() not in CONSONANTS:
            consonants.remove(c)
        c = c.capitalize()
    if not consonants:
        consonants = ['B', 'G', 'D']

    cv_syl = [c + v.lower() for c in consonants for v in vowels]
    all_syl = cv_syl + vowels

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
    while i < n_syl:
        if text == '' or text[-1].upper() not in VOWELS:
            text += random.choice(all_syl)
        else:
            text += random.choice(cv_syl)
        i += 1

    return text


def line() -> str:
    """Generate a line of 3-5 words, of up to 20 characters.

    Returns:
        str: A line of words up to 20 characters long, contructed from
        available CV and/or V syllables.
    """
    n_words = random.randint(3, 5)

    text = ''
    i = 0
    while i < n_words:
        text += word()
        if len(text) < 20:
            text += ' '
        i += 1

    if len(text) > 20:
        text = text[:text.rfind(' ')]

    return text


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "Abugida 3: Abugida Babalu (Einstürzende Zikkuraten)")
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
        log_name = 'babalu_' + now
        self.log_file = log_path/log_name

        select_lab = QLabel(' ')
        select_font = select_lab.font()
        select_font.setBold(True)
        select_font.setPixelSize(48)

        select_row = QHBoxLayout()
        layout.addLayout(select_row)

        vow_select = QGridLayout()
        select_row.addLayout(vow_select)
        vow_lab = QLabel('Vowels')
        vow_lab.setFont(select_font)
        vow_select.addWidget(vow_lab, 0, 0, 1, 6)
        for v in sorted(VOWELS):
            for col in range(len(SINGLE_VOWELS)):
                fam = sorted([vow for vow in VOWELS
                              if vow[0] == sorted(SINGLE_VOWELS)[col]])
                for row, item in enumerate(fam):
                    exec("vowCB_{} = QCheckBox('{}')"
                         .format(item.lower(), item))
                    exec("vow_select.addWidget(vowCB_{}, {}, {})"
                         .format(item.lower(), row + 1, col))

        con_select = QGridLayout()
        select_row.addLayout(con_select)
        con_lab = QLabel('Consonants')
        con_lab.setFont(select_font)
        con_select.addWidget(con_lab, 0, 0, 1, 6)
        con_rows = []
        for i in range(0, len(CONSONANTS), 6):
            con_rows.append(sorted(CONSONANTS)[i:i + 6])
        for row in range(len(con_rows)):
            for col, item in enumerate(con_rows[row]):
                exec("conCB_{} = QCheckBox('{}')"
                     .format(item.lower(), item))
                exec("con_select.addWidget(conCB_{}, {}, {})"
                     .format(item.lower(), row + 1, col))

        titles = ['Abugida Babalu', 'Einstüzende Zikkuraten']
        self.label = QLabel(random.choice(titles))
        lab_font = self.label.font()
        lab_font.setPixelSize(150)
        lab_font.setBold(True)
        lab_font.setFamily('Helvetica Ultra Compressed')
        self.label.setFont(lab_font)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedWidth(1150)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.btn = QPushButton(u'\u21BB')
        self.btn.clicked.connect(self.generate)
        btn_font = self.btn.font()
        btn_font.setPixelSize(120)
        btn_font.setBold(True)
        self.btn.setFont(btn_font)
        self.btn.setFixedWidth(150)
        layout.addWidget(self.btn, alignment=Qt.AlignCenter)

    def generate(self):
        this_line = line()
        self.label.setText(this_line)
        # with open(self.log_file, 'a') as f:
        #     f.write(this_line + '\n')


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
