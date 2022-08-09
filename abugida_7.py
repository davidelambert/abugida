import sys
import random
import subprocess
import shlex
from pathlib import Path
from tempfile import gettempdir
from typing import Union

from pySpeakNG import VOICES

from PyQt5.QtCore import (Qt,
                          QSize,
                          QRunnable,
                          QThreadPool,
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
LOOP = (u'\u146D', u'\u146B', u'\u146F', u'\u1472')
HOOK = (u'\u148B', u'\u1489', u'\u148D', u'\u1490')
BAR = (u'\u14A5', u'\u14A3', u'\u14A7', u'\u14AA')

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


def word(reflectionals=False):
    if reflectionals:
        shapes = [LOOP, HOOK, BAR]
    else:
        shapes = [DELTA, CHEVRON, ARCH]

    n_char = random.randint(2, 6)
    text = ''
    i = 0
    while i < n_char:
        con = random.choice([0, 1, 2])
        vow = random.choice([0, 1, 2, 3])
        text += shapes[con][vow]
        i += 1

    return text


def line(reflectionals=False):
    n_words = random.randint(2, 5)
    text = ''
    i = 0
    while i < n_words - 1:
        text = text + word(reflectionals) + ' '
        i += 1
    text += word(reflectionals)  # no space after last word
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
        self.setWindowTitle("Abugida 7")
        self.setMinimumSize(1300, 975)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setContentsMargins(50, 50, 50, 50)
        layout = QVBoxLayout()
        self.setLayout(layout)

        QFontDatabase.addApplicationFont(
            str(HERE/'fonts/FreeSansBold.ttf'))
        font = QFont('Free Sans')
        font.setPointSize(144)
        font.setWordSpacing(40)
        self.setFont(font)

        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abugida 7")
        self.setWindowIcon(QIcon(str(HERE/'img/abugida_icon.svg')))
        self.setMinimumSize(1300, 975)
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(50)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.log_on = False
        self.log_file = None
        self.threadpool = QThreadPool()

        # DESIGN CONSTANTS ================
        BW = 150    # button width
        BH = 40     # button height
        CSW = 400   # consonant QGroupBox width
        CSH = 120   # consonant QGroupBox height

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
        disp_font.setPointSize(72)
        disp_font.setWordSpacing(40)

        ipa_font = QFont('Free Sans')
        ipa_font.setPointSize(16)
        ipa_font.setWordSpacing(20)

        # DISPLAY ===========================
        self.disp_window = DisplayWindow()

        self.disp_cas = QLabel()
        self.disp_cas.setFont(disp_font)
        self.disp_cas.setWordWrap(True)
        self.disp_cas.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.disp_cas)

        # CONTROL LAYOUT GROUP =====================
        ctl_grp = QVBoxLayout()
        ctl_grp.setContentsMargins(25, 25, 25, 25)
        ctl_grp.setSpacing(32)

        # IPA DISPLAY ======================
        self.disp_ipa = QLabel()
        self.disp_ipa.setFont(ipa_font)
        self.disp_ipa.setWordWrap(True)
        self.disp_ipa.setAlignment(Qt.AlignCenter)
        ctl_grp.addWidget(self.disp_ipa)

        # CONSONANT SELECTION ==================
        con_sel = QHBoxLayout()
        con_sel.setSpacing(32)
        ctl_grp.addLayout(con_sel)

        # rotationals --------------------------
        rot_grid = QGridLayout()
        rot_grid.setAlignment(Qt.AlignCenter)
        rot_grid.setHorizontalSpacing(50)
        rot_grid.setVerticalSpacing(5)

        radio_rot = QRadioButton()
        radio_rot.setChecked(True)
        rot_grid.addWidget(radio_rot, 0, 0, 2, 1)

        delta_icon = QPixmap(str(HERE/'img/delta.svg'))
        delta_lab = QLabel()
        delta_lab.setPixmap(delta_icon)
        self.con_delta = random.choice(list(CON))
        self.delta_sel = QComboBox()
        self.delta_sel.addItems(list(CON))
        self.delta_sel.setCurrentText(self.con_delta)
        self.delta_sel.setFixedWidth(60)
        self.delta_sel.currentTextChanged.connect(self.set_delta)
        rot_grid.addWidget(delta_lab, 0, 1)
        rot_grid.addWidget(self.delta_sel, 1, 1)

        chevron_icon = QPixmap(str(HERE/'img/chevron.svg'))
        chevron_lab = QLabel()
        chevron_lab.setPixmap(chevron_icon)
        self.con_chevron = random.choice(list(CON))
        self.chevron_sel = QComboBox()
        self.chevron_sel.addItems(list(CON))
        self.chevron_sel.setCurrentText(self.con_chevron)
        self.chevron_sel.setFixedWidth(60)
        self.chevron_sel.currentTextChanged.connect(self.set_chevron)
        rot_grid.addWidget(chevron_lab, 0, 2)
        rot_grid.addWidget(self.chevron_sel, 1, 2)

        arch_icon = QPixmap(str(HERE/'img/arch.svg'))
        arch_lab = QLabel()
        arch_lab.setPixmap(arch_icon)
        self.con_arch = random.choice(list(CON))
        self.arch_sel = QComboBox()
        self.arch_sel.addItems(list(CON))
        self.arch_sel.setCurrentText(self.con_arch)
        self.arch_sel.setFixedWidth(60)
        self.arch_sel.currentTextChanged.connect(self.set_arch)
        rot_grid.addWidget(arch_lab, 0, 3)
        rot_grid.addWidget(self.arch_sel, 1, 3)

        rot_group = QGroupBox()
        rot_group.setFixedSize(CSW, CSH)
        rot_group.setLayout(rot_grid)
        con_sel.addWidget(rot_group)

        # reflectionals -------------------------
        ref_grid = QGridLayout()
        ref_grid.setAlignment(Qt.AlignCenter)
        ref_grid.setHorizontalSpacing(50)
        ref_grid.setVerticalSpacing(20)

        radio_ref = QRadioButton()
        ref_grid.addWidget(radio_ref, 0, 0, 2, 1)

        loop_icon = QPixmap(str(HERE/'img/loop.svg'))
        loop_lab = QLabel()
        loop_lab.setPixmap(loop_icon)
        self.con_loop = ''
        self.loop_sel = QComboBox()
        self.loop_sel.addItems(list(CON))
        self.loop_sel.setFixedWidth(60)
        self.loop_sel.currentTextChanged.connect(self.set_loop)
        ref_grid.addWidget(loop_lab, 0, 1)
        ref_grid.addWidget(self.loop_sel, 1, 1)

        hook_icon = QPixmap(str(HERE/'img/hook.svg'))
        hook_lab = QLabel()
        hook_lab.setPixmap(hook_icon)
        self.con_hook = ''
        self.hook_sel = QComboBox()
        self.hook_sel.addItems(list(CON))
        self.hook_sel.setFixedWidth(60)
        self.hook_sel.currentTextChanged.connect(self.set_hook)
        ref_grid.addWidget(hook_lab, 0, 2)
        ref_grid.addWidget(self.hook_sel, 1, 2)

        bar_icon = QPixmap(str(HERE/'img/bar.svg'))
        bar_lab = QLabel()
        bar_lab.setPixmap(bar_icon)
        self.con_bar = ''
        self.bar_sel = QComboBox()
        self.bar_sel.addItems(list(CON))
        self.bar_sel.setFixedWidth(60)
        self.bar_sel.currentTextChanged.connect(self.set_bar)
        ref_grid.addWidget(bar_lab, 0, 3)
        ref_grid.addWidget(self.bar_sel, 1, 3)

        ref_group = QGroupBox()
        ref_group.setFixedSize(CSW, CSH)
        ref_group.setLayout(ref_grid)
        con_sel.addWidget(ref_group)

        # radio button group control
        self.ref_switch = False  # default: rotational group
        self.rotref_grp = QButtonGroup()
        self.rotref_grp.addButton(radio_rot, id=0)  # self.ref_switch = False
        self.rotref_grp.addButton(radio_ref, id=1)  # self.ref_switch = True
        self.rotref_grp.buttonClicked.connect(self.set_ref_switch)

        # initial consonants and line
        self.random_consonants()
        self.new_line()

        # TEXT CONTROLS =============================
        text_row = QHBoxLayout()
        text_row.setAlignment(Qt.AlignCenter)
        ctl_grp.addLayout(text_row)

        btn_new = QPushButton('New Line')
        btn_new.setFixedSize(BW, BH)
        btn_new.clicked.connect(self.new_line)
        text_row.addWidget(btn_new)

        btn_randcon = QPushButton('Rand. Letters')
        btn_randcon.setFixedSize(BW, BH)
        btn_randcon.clicked.connect(self.random_consonants)
        text_row.addWidget(btn_randcon)

        btn_speak = QPushButton('Speak')
        btn_speak.setFixedSize(BW, BH)
        btn_speak.clicked.connect(self.speak)
        text_row.addWidget(btn_speak)

        btn_randvoice = QPushButton('Rand. Voice')
        btn_randvoice.setFixedSize(BW, BH)
        btn_randvoice.clicked.connect(self.random_voice)
        text_row.addWidget(btn_randvoice)

        self.btn_log = QPushButton('Text Log: OFF')
        self.btn_log.setCheckable(True)
        self.btn_log.clicked.connect(self.toggle_log)
        self.btn_log.setFixedSize(BW, BH)
        text_row.addWidget(self.btn_log)

        self.btn_ext = QPushButton('Display: OFF')
        self.btn_ext.setCheckable(True)
        self.btn_ext.clicked.connect(self.toggle_disp)
        self.btn_ext.setFixedSize(BW, BH)
        text_row.addWidget(self.btn_ext)

        # VOICE CONTROLS ===========================
        voice_row = QGridLayout()
        voice_row.setAlignment(Qt.AlignCenter)
        voice_row.setHorizontalSpacing(50)
        voice_row.setVerticalSpacing(0)
        ctl_grp.addLayout(voice_row)

        self.voice = random.choice(VOICES)
        self.ctl_voice = QComboBox()
        self.ctl_voice.addItems(sorted(VOICES, key=lambda x: x.lower()))
        self.ctl_voice.setCurrentText(self.voice)
        self.ctl_voice.setFixedWidth(BW)
        self.ctl_voice.currentTextChanged.connect(self.set_voice)
        lab_voice = QLabel('Voice')
        voice_row.addWidget(lab_voice, 0, 0, alignment=Qt.AlignBottom)
        voice_row.addWidget(self.ctl_voice, 1, 0)

        self.pitch = random.randint(0, 99)
        self.ctl_pitch = QSlider()
        self.ctl_pitch.setRange(0, 99)
        self.ctl_pitch.setValue(self.pitch)
        self.ctl_pitch.setOrientation(Qt.Horizontal)
        self.ctl_pitch.setFixedWidth(BW)
        self.ctl_pitch.valueChanged.connect(self.set_pitch)
        lab_pitch = QLabel('Pitch')
        voice_row.addWidget(lab_pitch, 0, 1, alignment=Qt.AlignBottom)
        voice_row.addWidget(self.ctl_pitch, 1, 1)

        self.speed = random.randint(25, 250)
        self.ctl_speed = QSlider()
        self.ctl_speed.setRange(25, 250)
        self.ctl_speed.setValue(self.speed)
        self.ctl_speed.setOrientation(Qt.Horizontal)
        self.ctl_speed.setFixedWidth(BW)
        self.ctl_speed.valueChanged.connect(self.set_speed)
        lab_speed = QLabel('Speed')
        voice_row.addWidget(lab_speed, 0, 2, alignment=Qt.AlignBottom)
        voice_row.addWidget(self.ctl_speed, 1, 2)

        self.gap = random.randint(1, 40)
        self.ctl_gap = QSlider()
        self.ctl_gap.setRange(1, 40)
        self.ctl_gap.setValue(self.gap)
        self.ctl_gap.setOrientation(Qt.Horizontal)
        self.ctl_gap.setFixedWidth(BW)
        self.ctl_gap.valueChanged.connect(self.set_gap)
        lab_gap = QLabel('Gap')
        voice_row.addWidget(lab_gap, 0, 3, alignment=Qt.AlignBottom)
        voice_row.addWidget(self.ctl_gap, 1, 3)

        self.amplitude = 50
        self.ctl_amplitude = QSlider()
        self.ctl_amplitude.setRange(0, 75)
        self.ctl_amplitude.setValue(self.amplitude)
        self.ctl_amplitude.setOrientation(Qt.Horizontal)
        self.ctl_amplitude.setFixedWidth(BW)
        self.ctl_amplitude.valueChanged.connect(self.set_amplitude)
        lab_amplitude = QLabel('Volume')
        voice_row.addWidget(lab_amplitude, 0, 4, alignment=Qt.AlignBottom)
        voice_row.addWidget(self.ctl_amplitude, 1, 4)

        ctl_box = QGroupBox()
        ctl_box.setLayout(ctl_grp)
        ctl_box.setFixedWidth(1200)
        layout.addWidget(ctl_box, alignment=Qt.AlignCenter)
        # ======= END __init__() =======

    def set_delta(self, s):
        self.con_delta = s

    def set_chevron(self, s):
        self.con_chevron = s

    def set_arch(self, s):
        self.con_arch = s

    def set_loop(self, s):
        self.con_loop = s

    def set_hook(self, s):
        self.con_hook = s

    def set_bar(self, s):
        self.con_bar = s

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

    def set_ref_switch(self):
        if self.rotref_grp.checkedId():
            self.ref_switch = True
            print('Reflectionals on.')
        else:
            self.ref_switch = False
            print('Rotationals on.')

    def random_consonants(self):
        sample = random.sample(list(CON), k=6)
        self.delta_sel.setCurrentText(sample[0])
        self.chevron_sel.setCurrentText(sample[1])
        self.arch_sel.setCurrentText(sample[2])
        self.loop_sel.setCurrentText(sample[3])
        self.hook_sel.setCurrentText(sample[4])
        self.bar_sel.setCurrentText(sample[5])

    def new_line(self):
        self.cas = line(self.ref_switch)
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
            elif char in LOOP:
                con = self.con_loop
                vow = list(VOW)[LOOP.index(char)]
                ipa = ipa + con + vow
            elif char in HOOK:
                con = self.con_hook
                vow = list(VOW)[HOOK.index(char)]
                ipa = ipa + con + vow
            elif char in BAR:
                con = self.con_bar
                vow = list(VOW)[BAR.index(char)]
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
