import sys
import random
import subprocess
import shlex
from pathlib import Path
from tempfile import gettempdir
from typing import Union
from string import ascii_uppercase

from pySpeakNG import speak as espeak
from pySpeakNG import LANGUAGES, VOICES

from PyQt5.QtCore import (Qt,
                          QSize,
                          QObject,
                          QRunnable,
                          QThreadPool,
                          pyqtSignal,
                          pyqtSlot)
from PyQt5.QtGui import (QIcon,
                         QPixmap,
                         QFontDatabase,
                         QFont)
from PyQt5.QtWidgets import *

HERE = Path(__file__).parent.resolve()
TMP = Path(gettempdir())

DELTA = (u'\u1403', u'\u1405', u'\u1401', u'\u140A')
CHEVRON = (u'\u1431', u'\u1433', u'\u142F', u'\u1438')
ARCH = (u'\u144E', u'\u1450', u'\u144C', u'\u1455')
KEYS = ['DELTA', 'CHEVRON', 'ARCH']
CHARSET = dict(zip(KEYS, [eval(k) for k in KEYS]))

CLAB = {'p': 'p', 'b': 'b', 'f': 'f', 'v': 'v', }
CDENT = {'θ': 'T', 'ð': 'D', }
CALV = {'t': 't', 'd': 'd', 's': 's', 'z': 'z', }
CPALV = {'tʃ': 'tS', 'dʒ': 'dZ', 'ʃ': 'S', 'ʒ': 'Z', }
CVEGL = {'k': 'k', 'g': 'g', 'h': 'h', }
CNAS = {'m': 'm', 'n': 'n', }
CAPP = {'l': 'l', 'r': 'r', 'j': 'j', 'w': 'w', }
CON = CLAB | CDENT | CALV | CPALV | CVEGL | CNAS | CAPP
VOW = {'i': 'i', 'o': 'o', 'e': 'e', 'a': 'a', }
CHARDICT = CON | VOW


def rlookup(val, d: dict) -> Union[str, None]:
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None


def word():
    n_char = random.randint(2, 6)
    text = ''
    i = 0
    while i < n_char:
        con = random.choice(['d', 'c', 'a'])
        vow = random.choice([0, 1, 2, 3])
        if con == 'd':
            text += DELTA[vow]
        elif con == 'c':
            text += CHEVRON[vow]
        else:
            text += ARCH[vow]
        i += 1

    return text


def line():
    n_words = random.randint(2, 5)
    text = ''
    i = 0
    while i < n_words - 1:
        text = text + word() + ' '
        i += 1
    text += word()  # no space after last word
    i += 1

    return text


def random_prosody(s):
    vowels = ['a', 'e', 'i', 'o']
    in_words = s.split()
    out_words = []
    for w in in_words:
        syllabized = ''
        for char in w:
            if char in vowels:
                if random.choice([True, False]):  # random vowel lengthening
                    syllabized = syllabized + char + ': '
                else:
                    syllabized = syllabized + char + ' '
            else:
                syllabized = syllabized + char

        syl = syllabized.split()
        if len(syl) == 1:
            if random.choice([True, False]):
                syl[0] = "'" + syl[0]
        elif len(syl) > 3:
            stress = random.sample(range(len(syl)), k=2)
            syl[stress[0]] = "'" + syl[stress[0]]
            syl[stress[1]] = "," + syl[stress[1]]
        else:
            stress = random.choice(range(len(syl)))
            syl[stress] = "'" + syl[stress]
        out_words.append(''.join(syl))

    return ' '.join(out_words)


class SpeechRunner(QRunnable):
    def __init__(self, voice, pitch, speed, gap, amplitude, text):
        super().__init__()
        # self.signals = WorkerSignals()
        self.voice = voice
        self.pitch = pitch
        self.speed = speed
        self.gap = gap,
        self.amplitude = amplitude
        self.text = "[[" + text + "]]"

    @pyqtSlot()
    def run(self):
        cmd_split = shlex.split(
            "espeak-ng -ven+{} -p {} -s {} -g {} -a {} \"{}\""
            .format(self.voice, self.pitch, self.speed, self.gap,
                    self.amplitude, self.text, ))

        subprocess.run(cmd_split)


class ShapeCB(QCheckBox):
    def __init__(self, key: str):
        super().__init__()
        self.key = key


class DisplayWindow(QWidget):
    def __init__(self, text=''):
        super().__init__()
        self.setWindowTitle("Abugida 5: Einstürzende Zikkuraten")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
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
        self.setWindowTitle("Abugida 6")
        self.setWindowIcon(QIcon(str(HERE/'img/abugida_icon.svg')))
        self.setMinimumSize(1300, 975)
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
        self.threadpool = QThreadPool()

        # TYPOGRAPHY =====================
        QFontDatabase.addApplicationFont(
            str(HERE/'fonts/FreeSans.ttf'))
        QFontDatabase.addApplicationFont(
            str(HERE/'fonts/FreeSansBold.ttf'))
        QFontDatabase.addApplicationFont(
            str(HERE/'fonts/FreeSansOblique.ttf'))
        QFontDatabase.addApplicationFont(
            str(HERE/'fonts/FreeSansBoldOblique.ttf'))

        font = QFont('Free Sans')
        container.setFont(font)

        disp_font = QFont('Free Sans')
        disp_font.setPointSize(30)
        disp_font.setWordSpacing(40)

        # LETTER SELECTIONS =========================
        select = QHBoxLayout()
        select.setSpacing(50)
        layout.addLayout(select)

        self.active = random.sample(KEYS, 3)
        init_cons = self.random_consonants()

        # CARDINALS ==========================
        card_grid = QGridLayout()
        card_grid.setAlignment(Qt.AlignCenter)
        card_grid.setHorizontalSpacing(50)
        card_grid.setVerticalSpacing(5)

        delta_icon = QPixmap(str(HERE/'img/delta.svg'))
        delta_lab = QLabel()
        delta_lab.setPixmap(delta_icon)
        self.con_delta = init_cons[0]
        self.delta_sel = QComboBox()
        self.delta_sel.addItems(list(CON))
        self.delta_sel.setCurrentText(self.con_delta)
        self.delta_sel.setFixedWidth(60)
        self.delta_sel.currentTextChanged.connect(self.set_delta)
        card_grid.addWidget(delta_lab, 0, 0)
        card_grid.addWidget(self.delta_sel, 1, 0)

        chevron_icon = QPixmap(str(HERE/'img/chevron.svg'))
        chevron_lab = QLabel()
        chevron_lab.setPixmap(chevron_icon)
        self.con_chevron = init_cons[1]
        self.chevron_sel = QComboBox()
        self.chevron_sel.addItems(list(CON))
        self.chevron_sel.setCurrentText(self.con_chevron)
        self.chevron_sel.setFixedWidth(60)
        self.chevron_sel.currentTextChanged.connect(self.set_chevron)
        card_grid.addWidget(chevron_lab, 0, 1)
        card_grid.addWidget(self.chevron_sel, 1, 1)

        arch_icon = QPixmap(str(HERE/'img/arch.svg'))
        arch_lab = QLabel()
        arch_lab.setPixmap(arch_icon)
        self.con_arch = init_cons[2]
        self.arch_sel = QComboBox()
        self.arch_sel.addItems(list(CON))
        self.arch_sel.setCurrentText(self.con_arch)
        self.arch_sel.setFixedWidth(60)
        self.arch_sel.currentTextChanged.connect(self.set_arch)
        card_grid.addWidget(arch_lab, 0, 2)
        card_grid.addWidget(self.arch_sel, 1, 2)

        card_group = QGroupBox()
        card_group.setMaximumWidth(500)
        card_group.setLayout(card_grid)
        select.addWidget(card_group)

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
        tbox.setFixedSize(800, 120)
        layout.addWidget(tbox, alignment=Qt.AlignCenter)

        # DISPLAY ===================================
        self.disp_cas = QLabel()
        self.disp_cas.setFont(disp_font)
        self.disp_cas.setWordWrap(True)
        self.disp_cas.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.disp_cas)

        self.disp_ipa = QLabel()
        self.disp_ipa.setFont(disp_font)
        self.disp_ipa.setWordWrap(True)
        self.disp_ipa.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.disp_ipa)

        self.disp_window = DisplayWindow()

        self.new_line()  # initital line

        # VOICE =====================
        voice_ctlgrp = QGridLayout()
        voice_ctlgrp.setAlignment(Qt.AlignCenter)
        voice_ctlgrp.setHorizontalSpacing(50)
        voice_ctlgrp.setVerticalSpacing(0)

        CTLW = 80

        self.voice = random.choice(VOICES)
        self.ctl_voice = QComboBox()
        self.ctl_voice.addItems(sorted(VOICES, key=lambda x: x.lower()))
        self.ctl_voice.setCurrentText(self.voice)
        self.ctl_voice.setFixedWidth(BW)
        self.ctl_voice.currentTextChanged.connect(self.set_voice)
        lab_voice = QLabel('Voice')
        voice_ctlgrp.addWidget(lab_voice, 0, 0, alignment=Qt.AlignBottom)
        voice_ctlgrp.addWidget(self.ctl_voice, 1, 0)

        self.pitch = random.randint(0, 99)
        self.ctl_pitch = QSlider()
        self.ctl_pitch.setRange(0, 99)
        self.ctl_pitch.setValue(self.pitch)
        self.ctl_pitch.setOrientation(Qt.Horizontal)
        self.ctl_pitch.setFixedWidth(CTLW)
        self.ctl_pitch.valueChanged.connect(self.set_pitch)
        lab_pitch = QLabel('Pitch')
        voice_ctlgrp.addWidget(lab_pitch, 0, 1, alignment=Qt.AlignBottom)
        voice_ctlgrp.addWidget(self.ctl_pitch, 1, 1)

        self.speed = random.randint(25, 250)
        self.ctl_speed = QSlider()
        self.ctl_speed.setRange(25, 250)
        self.ctl_speed.setValue(self.speed)
        self.ctl_speed.setOrientation(Qt.Horizontal)
        self.ctl_speed.setFixedWidth(CTLW)
        self.ctl_speed.valueChanged.connect(self.set_speed)
        lab_speed = QLabel('Speed')
        voice_ctlgrp.addWidget(lab_speed, 0, 2, alignment=Qt.AlignBottom)
        voice_ctlgrp.addWidget(self.ctl_speed, 1, 2)

        self.gap = random.randint(1, 40)
        self.ctl_gap = QSlider()
        self.ctl_gap.setRange(1, 40)
        self.ctl_gap.setValue(self.gap)
        self.ctl_gap.setOrientation(Qt.Horizontal)
        self.ctl_gap.setFixedWidth(CTLW)
        self.ctl_gap.valueChanged.connect(self.set_gap)
        lab_gap = QLabel('Gap')
        voice_ctlgrp.addWidget(lab_gap, 0, 3, alignment=Qt.AlignBottom)
        voice_ctlgrp.addWidget(self.ctl_gap, 1, 3)

        self.amplitude = 50
        self.ctl_amplitude = QSlider()
        self.ctl_amplitude.setRange(0, 75)
        self.ctl_amplitude.setValue(self.amplitude)
        self.ctl_amplitude.setOrientation(Qt.Horizontal)
        self.ctl_amplitude.setFixedWidth(CTLW)
        self.ctl_amplitude.valueChanged.connect(self.set_amplitude)
        lab_amplitude = QLabel('Volume')
        voice_ctlgrp.addWidget(lab_amplitude, 0, 4, alignment=Qt.AlignBottom)
        voice_ctlgrp.addWidget(self.ctl_amplitude, 1, 4)

        btn_randV = QPushButton('Randomize')
        btn_randV.setFixedSize(BW, BH)
        btn_randV.clicked.connect(self.random_voice)
        voice_ctlgrp.addWidget(btn_randV, 0, 5, 2, 1)

        btn_speak = QPushButton('Speak')
        btn_speak.setFixedSize(BW, BH)
        btn_speak.clicked.connect(self.speak)
        voice_ctlgrp.addWidget(btn_speak, 0, 6, 2, 1)

        vbox = QGroupBox()
        vbox.setLayout(voice_ctlgrp)
        vbox.setFixedSize(1200, 120)
        layout.addWidget(vbox, alignment=Qt.AlignCenter)

    @classmethod
    def random_consonants(cls):
        return random.sample(list(CON), k=3)

    def update(self):
        self.active.clear()
        for cb in self.checkboxes:
            if cb.isChecked():
                self.active.append(cb.key)

    def set_delta(self, s):
        self.con_delta = s

    def set_chevron(self, s):
        self.con_chevron = s

    def set_arch(self, s):
        self.con_arch = s

    def new_line(self):
        self.cas = line()
        self.translate()
        self.disp_cas.setText(self.cas)
        self.disp_ipa.setText(self.ipa)
        self.disp_window.label.setText(self.cas)
        if self.log_on:
            with open(self.log_file, 'a') as f:
                lines = self.cas + '\n' + self.ipa + '\n'
                f.write(lines)

    def translate(self):
        ipa = ''
        for char in self.cas:
            if char in DELTA:
                con = self.con_delta
                vow = list(VOW)[DELTA.index(char)]
                ipa = ipa + con + vow
            elif char in CHEVRON:
                con = self.con_chevron
                vow = list(VOW)[CHEVRON.index(char)]
                ipa = ipa + con + vow
            elif char in ARCH:
                con = self.con_arch
                vow = list(VOW)[ARCH.index(char)]
                ipa = ipa + con + vow
            else:
                ipa = ipa + ' '
        self.ipa = ipa
        self.xsampa = ''.join(
            [CHARDICT[char] if char in CHARDICT else ' ' for char in ipa])

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

    def set_pitch(self, n):
        self.pitch = n

    def set_speed(self, n):
        self.speed = n

    def set_gap(self, n):
        self.gap = n

    def set_amplitude(self, n):
        self.amplitude = n

    def random_voice(self):
        self.voice = random.choice(VOICES)
        self.ctl_voice.setCurrentText(self.voice)
        self.pitch = random.randint(0, 99)
        self.ctl_pitch.setValue(self.pitch)
        self.speed = random.randint(25, 250)
        self.ctl_speed.setValue(self.speed)
        self.gap = random.randint(1, 40)
        self.ctl_gap.setValue(self.gap)

    def speak(self):
        stressed = random_prosody(self.xsampa)
        self.runner = SpeechRunner(
            voice=self.voice,
            pitch=self.pitch,
            speed=self.speed,
            gap=self.gap,
            amplitude=self.amplitude,
            text=stressed
        )
        self.threadpool.start(self.runner)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
