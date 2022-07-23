import sys
import random
from datetime import datetime
from pathlib import Path
from string import ascii_uppercase

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

LETTERS = set(ascii_uppercase)
drop_cons = ['Q', 'C', 'X']
for c in drop_cons:
    LETTERS.remove(c)

SINGLE_VOWELS = set('AEIOU')
DIPHTONGS = {'Ai', 'Oi', 'Ow'}
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
        layout.setContentsMargins(20, 20, 20, 20)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # LOG ==========================================
        log_path = Path('./abugida_logs')
        if not log_path.exists():
            log_path.mkdir()
        now = datetime.now().strftime('%Y-%m-%d-%H:%M')
        log_name = 'babalu_' + now
        self.log_file = log_path/log_name

        # LETTER SELECTION ================================
        select_ncol = 11
        self.vow_active = random.sample(list(VOWELS), 3)
        self.con_active = random.sample(list(CONSONANTS), 3)

        select_vgrid = QGridLayout()
        self.vow_cb = []
        for n, v in enumerate(sorted(VOWELS)):
            exec("cb_{} = QCheckBox('{}')".format(v, v))
            if v in self.vow_active:
                exec("cb_{}.setCheckState(Qt.Checked)".format(v))
            exec("cb_{}.stateChanged.connect(self.update_vowels)".format(v))
            exec("select_vgrid.addWidget(cb_{}, 0, {})".format(v, n))
            exec("self.vow_cb.append(cb_{})".format(v))
        select_vow = QGroupBox('Vowels/Diphthongs')
        select_vow.setLayout(select_vgrid)
        layout.addWidget(select_vow)

        select_cgrid = QGridLayout()
        self.con_cb = []
        for n, c in enumerate(sorted(CONSONANTS)):
            exec("cb_{} = QCheckBox('{}')".format(c, c))
            if c in self.con_active:
                exec("cb_{}.setCheckState(Qt.Checked)".format(c))
            exec("cb_{}.stateChanged.connect(self.update_cons)".format(c))
            exec("self.con_cb.append(cb_{})".format(c))
            if n < select_ncol:
                exec("select_cgrid.addWidget(cb_{}, 0, {})".format(c, n))
            else:
                exec("select_cgrid.addWidget(cb_{}, 1, {})"
                     .format(c, n - select_ncol))
        select_con = QGroupBox('Consonants/Digraphs')
        select_con.setLayout(select_cgrid)
        layout.addWidget(select_con)

        # LINE DISPLAY ============================================
        init_line = line(vowels=self.vow_active, consonants=self.con_active)
        self.label = QLabel(init_line)
        lab_font = self.label.font()
        lab_font.setPixelSize(200)
        lab_font.setBold(True)
        lab_font.setFamily('Helvetica Ultra Compressed')
        lab_font.setWordSpacing(40)
        self.label.setFont(lab_font)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # GENERATE BUTTON ==========================================
        self.btn = QPushButton(u'\u21BB')
        self.btn.clicked.connect(self.generate)
        btn_font = self.btn.font()
        btn_font.setPixelSize(60)
        btn_font.setBold(True)
        self.btn.setFont(btn_font)
        self.btn.setFixedWidth(80)
        layout.addWidget(self.btn, alignment=Qt.AlignHCenter)

    def generate(self):
        this_line = line(vowels=self.vow_active, consonants=self.con_active)
        self.label.setText(this_line)

    def update_vowels(self):
        self.vow_active.clear()
        for cb in self.vow_cb:
            if cb.isChecked():
                self.vow_active.append(cb.text())

    def update_cons(self):
        self.con_active.clear()
        for cb in self.con_cb:
            if cb.isChecked():
                self.con_active.append(cb.text())


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
