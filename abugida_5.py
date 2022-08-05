import sys
import random
from pathlib import Path
from tempfile import gettempdir
from typing import Union

from pySpeakNG import speak as espeak
from pySpeakNG import LANGUAGES, VOICES
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

HERE = Path(__file__).parent.resolve()
TMP = Path(gettempdir())

CLAB = {'p': 'p', 'b': 'b', 'f': 'f', 'v': 'v', }
CDENT = {'θ': 'T', 'ð': 'D', }
CALV = {'t': 't', 'd': 'd', 's': 's', 'z': 'z', }
CPALV = {'tʃ': 'tS', 'dʒ': 'dZ', 'ʃ': 'S', 'ʒ': 'Z', }
CVEGL = {'k': 'k', 'g': 'g', 'x': 'x', 'h': 'h', }
CNAS = {'m': 'm', 'n': 'n', 'ŋ': 'N', }
CAPP = {'l': 'l', 'r': 'r', 'j': 'j', 'w': 'w', }
CON = CLAB | CDENT | CALV | CPALV | CVEGL | CNAS | CAPP

VA = {'æ': '{', 'ɑ': 'A', 'ɑː': 'A:', 'ɒ': 'Q', }
VE = {'e': 'e', 'ɛ': 'E', 'ə': '@', 'ɜ': '3', }
VI = {'ɪ': 'I', 'i': 'i', 'iː': 'i:', }
VO = {'ɔ': 'O', 'ɔː': 'O:', }
VU = {'ʌ': 'V', 'ʊ': 'U', 'u': 'u', 'uː': 'u:', }
VD1 = {'eɪ': 'eI', 'əʊ': '@U', 'oʊ': 'oU', }
VD2 = {'aɪ': 'aI', 'ɔɪ': 'OI', 'aʊ': 'aU', }
VOW = VA | VE | VI | VO | VU | VD1 | VD2

eng_keys = ['en-029', 'en-gb', 'en-gb-scotland', 'en-gb-x-gbclan',
            'en-gb-x-gbcwmd', 'en-gb-x-rp', 'en-us', ]
ENG = {k: LANGUAGES[k] for k in eng_keys}


def get_key(val, d: dict):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None


class Word:
    def __init__(self,
                 consonants: Union[list, None] = None,
                 vowels: Union[list, None] = None,
                 n_syl: Union[int, None] = None) -> None:

        max_syl = 5

        if not consonants:
            consonants = random.sample(list(CON.values()), k=3)
        con_xs = consonants.copy()
        con_ipa = [get_key(c, CON) for c in con_xs]

        if not vowels:
            vowels = random.sample(list(VOW.values()), k=3)
        vow_xs = vowels.copy()
        vow_ipa = [get_key(v, VOW) for v in vow_xs]

        if not n_syl:
            n_syl = random.randint(1, max_syl)

        if n_syl > max_syl:
            n_syl = n_syl % max_syl

        syl_xs = [c + v for c in con_xs for v in vow_xs] + vow_xs
        syl_ipa = [c + v for c in con_ipa for v in vow_ipa] + vow_ipa

        # random syllables
        draw = random.choices(range(len(syl_xs)), k=n_syl)
        self.syl_xsampa = [syl_xs[i] for i in draw]
        self.syl_ipa = [syl_ipa[i] for i in draw]

        # random prosody
        if len(draw) == 1:
            stress = random.choice([True, False])
            if stress:
                self.syl_xsampa[0] = "'" + self.syl_xsampa[0]
                self.syl_ipa[0] = "'" + self.syl_ipa[0]
        elif len(draw) > 3:
            stress = random.sample(range(len(self.syl_xsampa)), k=2)
            self.syl_xsampa[stress[0]] = "'" + self.syl_xsampa[stress[0]]
            self.syl_xsampa[stress[1]] = "," + self.syl_xsampa[stress[1]]
            self.syl_ipa[stress[0]] = "'" + self.syl_ipa[stress[0]]
            self.syl_ipa[stress[1]] = "," + self.syl_ipa[stress[1]]
        else:
            stress = random.choice(range(len(self.syl_xsampa)))
            self.syl_xsampa[stress] = "'" + self.syl_xsampa[stress]
            self.syl_ipa[stress] = "'" + self.syl_ipa[stress]

        # word representaions from syllables
        self.xsampa = ''.join(self.syl_xsampa)
        self.ipa = ''.join(self.syl_ipa)

    def __repr__(self) -> str:
        return self.ipa

    def __str__(self) -> str:
        return self.xsampa


class Line:
    def __init__(self,
                 consonants: Union[list, None] = None,
                 vowels: Union[list, None] = None,
                 n_words: Union[int, None] = None) -> None:

        max_words = 5

        if not consonants:
            consonants = random.sample(list(CON.values()), k=3)

        if not vowels:
            vowels = random.sample(list(VOW.values()), k=3)

        if not n_words:
            n_words = random.randint(1, max_words)
        if n_words < 1:
            n_words = 1
        if n_words > max_words:
            n_words = n_words % max_words
        self.n_words = n_words

        self.words = [Word(consonants=consonants, vowels=vowels)
                      for i in range(n_words)]
        self.xsampa = ' '.join([w.xsampa for w in self.words])
        self.ipa = ' '.join([w.ipa for w in self.words])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abugida 5: Einstürzende Zikkuraten")
        self.setWindowIcon(QIcon(str(HERE/'img/abugida_icon.svg')))
        self.showMaximized()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        BW = 160  # Button Width
        BH = 40   # Button Height
        self.log_on = False
        self.log_file = None

        # LETTER SELECTION ================================
        select = QHBoxLayout()
        select.setContentsMargins(50, 0, 50, 0)
        layout.addLayout(select)

        self.vow_active = random.sample(list(VOW.values()), 3)
        self.con_active = random.sample(list(CON.values()), 3)

        # CONSONANTS =============================================
        cgrid = QGridLayout()
        cgrid.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        cgrid.setContentsMargins(20, 20, 20, 20)
        cgrid.setHorizontalSpacing(50)
        cgrid.setVerticalSpacing(25)

        self.con_cb = []
        con_dicts = [CLAB, CDENT, CALV, CPALV, CVEGL, CNAS, CAPP]
        for lset in con_dicts:
            for ipa, xsampa in lset.items():
                exec("self.cb_{} = QCheckBox('{}')".format(xsampa, ipa))
                if xsampa in self.con_active:
                    exec("self.cb_{}.setCheckState(Qt.Checked)".format(xsampa))
                exec("self.cb_{}.stateChanged.connect(self.update_con)"
                     .format(xsampa))
                exec("cgrid.addWidget(self.cb_{}, {}, {})"
                     .format(xsampa, con_dicts.index(lset),
                             list(lset).index(ipa)))
                exec("self.con_cb.append(self.cb_{})".format(xsampa))

        cgroup = QGroupBox('Consonants')
        cgroup.setLayout(cgrid)
        cgroup.setFixedSize(400, 400)
        select.addWidget(cgroup, alignment=Qt.AlignTop)

        # VOWELS =============================================
        vgrid = QGridLayout()
        vgrid.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        vgrid.setContentsMargins(20, 20, 20, 20)
        vgrid.setHorizontalSpacing(50)
        vgrid.setVerticalSpacing(25)

        self.vow_cb = []
        vow_dicts = [VA, VE, VI, VO, VU, VD1, VD2, ]
        for lset in vow_dicts:
            for ipa, xsampa in lset.items():
                if xsampa == '{':
                    xsampa = 'ae'
                if xsampa.endswith(':'):
                    xsampa = xsampa[0] + xsampa[0]
                if '@' in xsampa:
                    xsampa = xsampa.replace('@', 'uh')
                exec("self.cb_{} = QCheckBox('{}')".format(xsampa, ipa))
                if xsampa in self.vow_active:
                    exec("self.cb_{}.setCheckState(Qt.Checked)".format(xsampa))
                exec("self.cb_{}.stateChanged.connect(self.update_vow)"
                     .format(xsampa))
                exec("vgrid.addWidget(self.cb_{}, {}, {})"
                     .format(xsampa, vow_dicts.index(lset),
                             list(lset).index(ipa)))
                exec("self.vow_cb.append(self.cb_{})".format(xsampa))

        vgroup = QGroupBox('Vowels')
        vgroup.setLayout(vgrid)
        vgroup.setFixedSize(400, 400)
        select.addWidget(vgroup, alignment=Qt.AlignTop)

    def update_con(self):
        pass

    def update_vow(self):
        pass


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
