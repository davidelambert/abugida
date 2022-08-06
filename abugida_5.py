import sys
import random
from pathlib import Path
from tempfile import gettempdir
from typing import Union
from string import ascii_uppercase

from pySpeakNG import speak as espeak
from pySpeakNG import LANGUAGES, VOICES
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFontDatabase, QFont
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

CKEY = [{'p': 'Pit', 'b': 'Bit', 'f': 'Fat', 'v': 'Vat', },
        {'θ': 'THigh', 'ð': 'THy', },
        {'t': 'Tin', 'd': 'Din', 's': 'Sap', 'z': 'Zap', },
        {'tʃ': 'CHeap', 'dʒ': 'Jeep', 'ʃ': 'raSH', 'ʒ': 'raJ', },
        {'k': 'Cut', 'g': 'Gut', 'x': 'loCH', 'h': 'Ham', },
        {'m': 'tiM', 'n': 'tiN', 'ŋ': 'tiNG', },
        {'l': 'Lump', 'r': 'Rump', 'j': 'Your', 'w': 'Wore'}]

VA = {'æ': 'a', 'ɑː': 'A:', }
VE = {'e': 'e', 'ɛ': 'E', 'ə': '@', 'ɜ': '3', }
VI = {'ɪ': 'I', 'iː': 'i:', }
VO = {'ɔ': 'O', 'ɔː': 'O:', }
VU = {'ʌ': 'V', 'ʊ': 'U', 'u': 'u', 'uː': 'u:', }
VD1 = {'eɪ': 'eI', 'aɪ': 'aI', }
VD2 = {'oʊ': 'oU', 'ɔɪ': 'OI', 'aʊ': 'aU', }
VOW = VA | VE | VI | VO | VU | VD1 | VD2

VKEY = [{'æ': 'trAp', 'ɑː': 'pAlm ', },
        {'e': 'drEss (brit)', 'ɛ': 'drEss (amer)',
         'ə': 'commA', 'ɜ': 'nUrse', },
        {'ɪ': 'kIt', 'iː': 'flEEce', },
        {'ɔ': 'tOt', 'ɔː': 'tAUGHt', },
        {'ʌ': 'strUt', 'ʊ': 'fOOt', 'u': 'lOse', 'uː': 'lOOse', },
        {'eɪ': 'fAce', 'aɪ': 'prIce', },
        {'oʊ': 'gOAt', 'ɔɪ': 'chOIce', 'aʊ': 'mOUth', }]

eng_keys = ['en-029', 'en-gb', 'en-gb-scotland', 'en-gb-x-gbclan',
            'en-gb-x-gbcwmd', 'en-gb-x-rp', 'en-us', ]
ENG = {k: LANGUAGES[k] for k in eng_keys}


def rlookup(val, d: dict) -> Union[str, None]:
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None


def embolden(s: str) -> str:
    output = ''
    for char in s:
        if char in ascii_uppercase:
            char = '<b>' + char.lower() + '</b>'
        output += char
    return output


class Word:
    def __init__(self,
                 consonants: Union[list, None] = None,
                 vowels: Union[list, None] = None,
                 n_syl: Union[int, None] = None) -> None:

        max_syl = 5

        if not consonants:
            consonants = random.sample(list(CON.values()), k=3)
        con_xs = consonants.copy()
        con_ipa = [rlookup(c, CON) for c in con_xs]

        if not vowels:
            vowels = random.sample(list(VOW.values()), k=3)
        vow_xs = vowels.copy()
        vow_ipa = [rlookup(v, VOW) for v in vow_xs]

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
                self.syl_ipa[0] = "ˈ" + self.syl_ipa[0]
        elif len(draw) > 3:
            stress = random.sample(range(len(self.syl_xsampa)), k=2)
            self.syl_xsampa[stress[0]] = "'" + self.syl_xsampa[stress[0]]
            self.syl_xsampa[stress[1]] = "," + self.syl_xsampa[stress[1]]
            self.syl_ipa[stress[0]] = "ˈ" + self.syl_ipa[stress[0]]
            self.syl_ipa[stress[1]] = "ˌ" + self.syl_ipa[stress[1]]
        else:
            stress = random.choice(range(len(self.syl_xsampa)))
            self.syl_xsampa[stress] = "'" + self.syl_xsampa[stress]
            self.syl_ipa[stress] = "ˈ" + self.syl_ipa[stress]

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


class KeyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Pronunciation Key')
        layout = QHBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(150)
        self.setLayout(layout)

        QFontDatabase.addApplicationFont(
            str(HERE/'gentium/GentiumBookPlus-Regular.ttf'))
        QFontDatabase.addApplicationFont(
            str(HERE/'gentium/GentiumBookPlus-Bold.ttf'))
        QFontDatabase.addApplicationFont(
            str(HERE/'gentium/GentiumBookPlus-Italic.ttf'))
        QFontDatabase.addApplicationFont(
            str(HERE/'gentium/GentiumBookPlus-BoldItalic.ttf'))
        font = QFont('Gentium Book Plus')
        font.setPointSize(14)
        self.setFont(font)

        cgrid = QGridLayout()
        cgrid.setHorizontalSpacing(50)
        cgrid.setVerticalSpacing(20)
        layout.addLayout(cgrid)

        ctitle = QLabel('<h3>Consonants</h3>')
        cgrid.addWidget(ctitle, 0, 0, 1, 2)

        for i in range(len(CKEY)):
            for j in range(len(CKEY[i])):
                ij = str(i) + str(j)
                k = list(CKEY[i].keys())[j]
                v = list(CKEY[i].values())[j]
                exec("kl_c{} = QLabel('{} = {}')".format(ij, k, embolden(v)))
                exec("cgrid.addWidget(kl_c{}, {}, {})".format(ij, i + 1, j))

        vgrid = QGridLayout()
        vgrid.setHorizontalSpacing(50)
        vgrid.setVerticalSpacing(20)
        layout.addLayout(vgrid)

        vtitle = QLabel('<h3>Vowels</h3>')
        vgrid.addWidget(vtitle, 0, 0, 1, 2)

        for i in range(len(VKEY)):
            for j in range(len(VKEY[i])):
                ij = str(i) + str(j)
                k = list(VKEY[i].keys())[j]
                v = list(VKEY[i].values())[j]
                exec("kl_v{} = QLabel('{} = {}')".format(ij, k, embolden(v)))
                exec("vgrid.addWidget(kl_v{}, {}, {})".format(ij, i + 1, j))


class DisplayWindow(QWidget):
    def __init__(self, text=''):
        super().__init__()
        self.setWindowTitle("Abugida 5: Einstürzende Zikkuraten")
        self.setContentsMargins(50, 50, 50, 50)
        layout = QVBoxLayout()
        self.setLayout(layout)

        QFontDatabase.addApplicationFont(
            str(HERE/'gentium/GentiumBookPlus-Bold.ttf'))
        font = QFont('Gentium Book Plus')
        font.setBold(True)
        font.setPointSize(72)
        font.setWordSpacing(40)
        self.setFont(font)

        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setMinimumSize(1200, 400)
        layout.addWidget(self.label)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abugida 5: Einstürzende Zikkuraten")
        self.setWindowIcon(QIcon(str(HERE/'img/abugida_icon.svg')))
        self.setMinimumSize(1300, 900)
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(50)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        BW = 160  # Button Width
        BH = 40   # Button Height
        self.log_on = False
        self.log_file = None
        self.key_window = KeyWindow()

        # TYPOGRAPHY =====================
        QFontDatabase.addApplicationFont(
            str(HERE/'gentium/GentiumBookPlus-Regular.ttf'))
        QFontDatabase.addApplicationFont(
            str(HERE/'gentium/GentiumBookPlus-Bold.ttf'))
        QFontDatabase.addApplicationFont(
            str(HERE/'gentium/GentiumBookPlus-Italic.ttf'))
        QFontDatabase.addApplicationFont(
            str(HERE/'gentium/GentiumBookPlus-BoldItalic.ttf'))

        font = QFont('Gentium Book Plus')
        font.setPointSize(14)
        container.setFont(font)

        disp_font = QFont('Gentium Plus')
        disp_font.setPointSize(30)
        disp_font.setWordSpacing(20)

        # LETTER SELECTION ================================
        select = QHBoxLayout()
        select.setSpacing(50)
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
                exec("self.cb_{} = QCheckBox('{}')"
                     .format(xsampa, ipa))
                if xsampa in self.con_active:
                    exec("self.cb_{}.setCheckState(Qt.Checked)"
                         .format(xsampa))
                exec("self.cb_{}.stateChanged.connect(self.update_con)"
                     .format(xsampa))
                exec("cgrid.addWidget(self.cb_{}, {}, {})"
                     .format(xsampa, con_dicts.index(lset),
                             list(lset).index(ipa)))
                exec("self.con_cb.append(self.cb_{})"
                     .format(xsampa))

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
                xsampa = self.replace_vow(xsampa)
                exec("self.cb_{} = QCheckBox('{}')"
                     .format(xsampa, ipa))
                if xsampa in self.vow_active:
                    exec("self.cb_{}.setCheckState(Qt.Checked)"
                         .format(xsampa))
                exec("self.cb_{}.stateChanged.connect(self.update_vow)"
                     .format(xsampa))
                exec("vgrid.addWidget(self.cb_{}, {}, {})"
                     .format(xsampa, vow_dicts.index(lset),
                             list(lset).index(ipa)))
                exec("self.vow_cb.append(self.cb_{})"
                     .format(xsampa))

        vgroup = QGroupBox('Vowels')
        vgroup.setLayout(vgrid)
        vgroup.setFixedSize(400, 400)
        select.addWidget(vgroup, alignment=Qt.AlignTop)

        # LETTER CONTROLS ================================
        btn_grid = QVBoxLayout()
        btn_grid.setAlignment(Qt.AlignCenter)
        btn_grid.setSpacing(25)

        btn_all = QPushButton('Select All')
        btn_all.setFixedSize(BW, BH)
        btn_all.clicked.connect(self.select_all)
        btn_grid.addWidget(btn_all)

        btn_none = QPushButton('Select None')
        btn_none.setFixedSize(BW, BH)
        btn_none.clicked.connect(self.select_none)
        btn_grid.addWidget(btn_none)

        btn_randL = QPushButton('Random (3C/3V)')
        btn_randL.setFixedSize(BW, BH)
        btn_randL.clicked.connect(self.random_letters)
        btn_grid.addWidget(btn_randL)

        btn_key = QPushButton('Show Key')
        btn_key.setFixedSize(BW, BH)
        btn_key.clicked.connect(self.show_key)
        btn_grid.addWidget(btn_key)

        btn_ctlgrp = QGroupBox('Control')
        btn_ctlgrp.setLayout(btn_grid)
        btn_ctlgrp.setFixedSize(200, 400)
        select.addWidget(btn_ctlgrp)

        # TEXT ======================
        tgrp = QHBoxLayout()
        tgrp.setAlignment(Qt.AlignCenter)
        tgrp.setSpacing(25)

        btn_new = QPushButton('New Line')
        btn_new.setFixedSize(BW, BH)
        btn_new.clicked.connect(self.new_line)
        tgrp.addWidget(btn_new)

        self.btn_log = QPushButton('Text Log: OFF')
        self.btn_log.setCheckable(True)
        self.btn_log.clicked.connect(self.toggle_log)
        self.btn_log.setFixedSize(BW, BH)
        tgrp.addWidget(self.btn_log)

        self.btn_ext = QPushButton('Display: OFF')
        self.btn_ext.setCheckable(True)
        self.btn_ext.clicked.connect(self.toggle_disp)
        self.btn_ext.setFixedSize(BW, BH)
        tgrp.addWidget(self.btn_ext)

        tbox = QGroupBox()
        tbox.setLayout(tgrp)
        tbox.setFixedSize(1000, 100)
        layout.addWidget(tbox, alignment=Qt.AlignCenter)

        # DISPLAY ===========================
        self.line = Line(consonants=self.con_active, vowels=self.vow_active)
        self.display = QLabel(self.line.ipa)

        self.disp_window = DisplayWindow()  # external display window
        self.disp_window.label.setText(self.line.ipa)

        self.display.setFont(disp_font)
        self.display.setWordWrap(True)
        # self.display.setMinimumHeight(300)
        self.display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.display)

        # VOICE =====================
        vgrp = QHBoxLayout()
        vgrp.setAlignment(Qt.AlignCenter)
        vgrp.setSpacing(25)

        voice_grid = QVBoxLayout()
        voice_grid.setSpacing(2)
        voice_grid.setAlignment(Qt.AlignBottom)
        voice_opt = sorted(VOICES + ['(Random)'], key=lambda x: x.lower())
        self.voice = '(Random)'
        voice_lab = QLabel('Voice')
        voice_sel = QComboBox()
        voice_sel.addItems(voice_opt)
        voice_sel.setCurrentText(self.voice)
        voice_sel.setFixedWidth(BW)
        voice_sel.currentTextChanged.connect(self.set_voice)
        voice_grid.addWidget(voice_lab)
        voice_grid.addWidget(voice_sel)
        vgrp.addLayout(voice_grid)

        speed_grid = QVBoxLayout()
        speed_grid.setSpacing(2)
        speed_grid.setAlignment(Qt.AlignBottom)
        speed_opt = ['(Random)', 'Slow', 'Medium', 'Fast']
        self.speed = '(Random)'
        speed_lab = QLabel('Speed')
        speed_sel = QComboBox()
        speed_sel.addItems(speed_opt)
        speed_sel.setCurrentText(self.speed)
        speed_sel.setFixedWidth(BW)
        speed_sel.currentTextChanged.connect(self.set_speed)
        speed_grid.addWidget(speed_lab)
        speed_grid.addWidget(speed_sel)
        vgrp.addLayout(speed_grid)

        pitch_grid = QVBoxLayout()
        pitch_grid.setSpacing(2)
        pitch_grid.setAlignment(Qt.AlignBottom)
        pitch_opt = ['(Random)', 'Low', 'Middle', 'High']
        self.pitch = '(Random)'
        pitch_lab = QLabel('Pitch')
        pitch_sel = QComboBox()
        pitch_sel.addItems(pitch_opt)
        pitch_sel.setCurrentText(self.pitch)
        pitch_sel.setFixedWidth(BW)
        pitch_sel.currentTextChanged.connect(self.set_pitch)
        pitch_grid.addWidget(pitch_lab)
        pitch_grid.addWidget(pitch_sel)
        vgrp.addLayout(pitch_grid)

        btn_speak = QPushButton('Speak')
        btn_speak.setFixedSize(BW, BH)
        btn_speak.clicked.connect(self.speak)
        vgrp.addWidget(btn_speak, alignment=Qt.AlignBottom)

        btn_sing = QPushButton('Sing')
        btn_sing.setFixedSize(BW, BH)
        btn_sing.clicked.connect(self.sing)
        vgrp.addWidget(btn_sing, alignment=Qt.AlignBottom)

        vbox = QGroupBox()
        vbox.setLayout(vgrp)
        vbox.setFixedSize(1000, 120)
        layout.addWidget(vbox, alignment=Qt.AlignCenter)

    @classmethod
    def replace_vow(cls, v):
        if v == '{':
            v = 'ae'
        if v.endswith(':'):
            v = v[0] + v[0]
        if '@' in v:
            v = v.replace('@', 'uh')
        return v

    def update_con(self):
        self.con_active.clear()
        for cb in self.con_cb:
            if cb.isChecked():
                self.con_active.append(CON[cb.text()])

    def update_vow(self):
        self.vow_active.clear()
        for cb in self.vow_cb:
            if cb.isChecked():
                self.vow_active.append(VOW[cb.text()])

    def select_all(self):
        for v in list(VOW.values()):
            v = self.replace_vow(v)
            exec("self.cb_{}.setCheckState(Qt.Checked)".format(v))
        for c in list(CON.values()):
            exec("self.cb_{}.setCheckState(Qt.Checked)".format(c))

    def select_none(self):
        for v in list(VOW.values()):
            v = self.replace_vow(v)
            exec("self.cb_{}.setCheckState(Qt.Unchecked)".format(v))
        for c in list(CON.values()):
            exec("self.cb_{}.setCheckState(Qt.Unchecked)".format(c))

    def random_letters(self):
        self.select_none()
        vsamp = random.sample(list(VOW.values()), k=3)
        for v in vsamp:
            v = self.replace_vow(v)
            exec("self.cb_{}.setCheckState(Qt.Checked)".format(v))
        csamp = random.sample(list(CON.values()), k=3)
        for c in csamp:
            exec("self.cb_{}.setCheckState(Qt.Checked)".format(c))

    def show_key(self):
        if not self.key_window.isVisible():
            self.key_window.show()

    def new_line(self):
        self.line = Line(consonants=self.con_active, vowels=self.vow_active)
        self.display.setText(self.line.ipa)
        self.disp_window.label.setText(self.line.ipa)
        if self.log_on:
            with open(self.log_file, 'a') as f:
                f.write(self.line.ipa + '\n')

    def toggle_log(self, checked):
        if not self.log_file:
            self.log_file = QFileDialog.getSaveFileName(
                self, directory=str(Path.home()))[0]
        self.log_on = checked
        if checked:
            self.btn_log.setText('Text Log: ON')
        else:
            self.btn_log.setText('Text Log: OFF')

    def toggle_disp(self, checked):
        if checked:
            self.btn_ext.setText('Display: ON')
            if not self.disp_window.isVisible():
                self.disp_window.show()
        else:
            self.btn_ext.setText('Display: OFF')
            if self.disp_window.isVisible():
                self.disp_window.hide()

    def set_voice(self, s):
        self.voice = s

    def set_speed(self, s):
        self.speed = s

    def set_pitch(self, s):
        self.pitch = s

    def speak(self):
        if self.voice == '(Random)':
            vopt = random.choice(VOICES)
        else:
            vopt = self.voice

        if self.speed == 'Slow':
            sopt = random.randint(25, 100)
            gopt = random.randint(26, 40)
        elif self.speed == 'Medium':
            sopt = random.randint(100, 175)
            gopt = random.randint(13, 26)
        elif self.speed == 'Fast':
            sopt = random.randint(175, 250)
            gopt = random.randint(1, 13)
        else:  # for default: '(Random)'
            sopt = random.randint(25, 250)
            gopt = random.randint(1, 40)

        if self.pitch == 'Low':
            popt = random.randint(0, 33)
        elif self.pitch == 'Middle':
            popt = random.randint(33, 66)
        elif self.pitch == 'High':
            popt = random.randint(66, 99)
        else:
            popt = random.randint(0, 99)

        print(self.line.xsampa)

        espeak("[[{}]]".format(self.line.xsampa), language='en-us',
               voice=vopt, pitch=popt, speed=sopt, gap=gopt)

    def sing(self):
        pass


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
