import sys
import random
from pathlib import Path
from tempfile import gettempdir

from pySpeakNG import speak as espeak
from pySpeakNG import LANGUAGES, VOICES
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

HERE = Path(__file__).parent.resolve()
TMP = Path(gettempdir())

VOW = {'A': 'a', 'U': 'u', 'I': 'i:', 'Au': 'aU', 'Ai': 'aI', 'Ui': 'wi:'}
CON = {'B': 'b', 'G': 'g', 'D': 'd'}
SYL_DISP = [c + v.lower() for c in list(CON) for v in list(VOW)]
SYL_PHON = [c + v for c in CON.values() for v in VOW.values()]


def rand_args():
    args = {
        'voice': random.choice(VOICES),
        'pitch': random.randint(0, 100),
        'speed': random.randint(30, 200)
    }

    return args


class Word:
    def __init__(self, n_syl: int | None = None) -> None:
        if not n_syl:
            n_syl = random.randint(1, 5)

        draw = random.choices(range(len(SYL_DISP)), k=n_syl)

        self.syl_disp = [SYL_DISP[i] for i in draw]
        self.display = ''.join(self.syl_disp)
        self.text = ''.join(self.syl_disp)

        self.syl = [SYL_PHON[i] for i in draw]
        if len(self.syl) == 1:
            stress = random.choice([True, False])
            if stress:
                self.syl[0] = "'" + self.syl[0]
        elif len(self.syl) > 3:
            stress1, stress2 = random.sample(range(len(self.syl)), k=2)
            self.syl[stress1] = "'" + self.syl[stress1]
            self.syl[stress2] = "," + self.syl[stress2]
        else:
            stress1 = random.choice(range(len(self.syl)))
            self.syl[stress1] = "'" + self.syl[stress1]

        self.phonetic = ''.join(self.syl)

    def __repr__(self) -> str:
        return self.text

    def __str__(self) -> str:
        return self.phonetic


class Line:
    def __init__(self, n_words: None | int = None,
                 n_syl: None | tuple[int] = None) -> None:

        if not n_words and not n_syl:
            n_words = random.randint(1, 5)
            n_syl = [None] * n_words

        if n_words and not n_syl:
            n_syl = [None] * n_words

        if not n_syl and not n_words:
            n_words = len(n_syl)

        self.objects = [Word(n_syl=n_syl[w]) for w in range(n_words)]
        self.words = [str(obj) for obj in self.objects]
        self.phonetic = ' '.join(self.words)
        self.display = ' '.join([obj.display for obj in self.objects])
        self.text = self.display.replace('-', '')

    def __repr__(self) -> str:
        return self.text

    def __str__(self) -> str:
        return self.phonetic


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abugida 2: Vogon Poetry")
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

        # VOICE CONTROL GROUP ===============================
        voice_ctlgrp = QGridLayout()
        voice_ctlgrp.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        voice_ctlgrp.setHorizontalSpacing(50)
        layout.addLayout(voice_ctlgrp)

        CTLW = 200  # control width

        self.language = 'en-us'
        lang_display = list(LANGUAGES.values())
        self.ctl_lang = QComboBox()
        self.ctl_lang.addItems(lang_display)
        self.ctl_lang.setCurrentText(LANGUAGES[self.language])
        self.ctl_lang.setFixedWidth(CTLW)
        self.ctl_lang.currentTextChanged.connect(self.set_lang)
        lab_lang = QLabel('Language')
        voice_ctlgrp.addWidget(lab_lang, 0, 0, alignment=Qt.AlignBottom)
        voice_ctlgrp.addWidget(self.ctl_lang, 1, 0)

        self.voice = random.choice(VOICES)
        self.ctl_voice = QComboBox()
        self.ctl_voice.addItems(sorted(VOICES, key=lambda x: x.lower()))
        self.ctl_voice.setCurrentText(self.voice)
        self.ctl_voice.setFixedWidth(CTLW)
        self.ctl_voice.currentTextChanged.connect(self.set_voice)
        lab_voice = QLabel('Voice')
        voice_ctlgrp.addWidget(lab_voice, 0, 1, alignment=Qt.AlignBottom)
        voice_ctlgrp.addWidget(self.ctl_voice, 1, 1)

        self.pitch = random.randint(0, 99)
        self.ctl_pitch = QSlider()
        self.ctl_pitch.setRange(0, 99)
        self.ctl_pitch.setValue(self.pitch)
        self.ctl_pitch.setOrientation(Qt.Horizontal)
        self.ctl_pitch.setFixedWidth(CTLW)
        self.ctl_pitch.valueChanged.connect(self.set_pitch)
        lab_pitch = QLabel('Pitch Adj.')
        voice_ctlgrp.addWidget(lab_pitch, 0, 2, alignment=Qt.AlignBottom)
        voice_ctlgrp.addWidget(self.ctl_pitch, 1, 2)

        self.speed = random.randint(25, 250)
        self.ctl_speed = QSlider()
        self.ctl_speed.setRange(25, 250)
        self.ctl_speed.setValue(self.speed)
        self.ctl_speed.setOrientation(Qt.Horizontal)
        self.ctl_speed.setFixedWidth(CTLW)
        self.ctl_speed.valueChanged.connect(self.set_speed)
        lab_speed = QLabel('Speed')
        voice_ctlgrp.addWidget(lab_speed, 0, 3, alignment=Qt.AlignBottom)
        voice_ctlgrp.addWidget(self.ctl_speed, 1, 3)

        self.gap = random.randint(1, 40)
        self.ctl_gap = QSlider()
        self.ctl_gap.setRange(1, 40)
        self.ctl_gap.setValue(self.gap)
        self.ctl_gap.setOrientation(Qt.Horizontal)
        self.ctl_gap.setFixedWidth(CTLW)
        self.ctl_gap.valueChanged.connect(self.set_gap)
        lab_gap = QLabel('Gap')
        voice_ctlgrp.addWidget(lab_gap, 0, 4, alignment=Qt.AlignBottom)
        voice_ctlgrp.addWidget(self.ctl_gap, 1, 4)

        self.amplitude = 50
        self.ctl_amplitude = QSlider()
        self.ctl_amplitude.setRange(0, 75)
        self.ctl_amplitude.setValue(self.amplitude)
        self.ctl_amplitude.setOrientation(Qt.Horizontal)
        self.ctl_amplitude.setFixedWidth(CTLW)
        self.ctl_amplitude.valueChanged.connect(self.set_amplitude)
        lab_amplitude = QLabel('Volume')
        voice_ctlgrp.addWidget(lab_amplitude, 0, 5, alignment=Qt.AlignBottom)
        voice_ctlgrp.addWidget(self.ctl_amplitude, 1, 5)

        # VOICE BUTTON GROUP =========================
        voice_btngrp = QHBoxLayout()
        voice_btngrp.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        voice_btngrp.setSpacing(50)
        layout.addLayout(voice_btngrp)

        self.btn_random = QPushButton('Randomize')
        self.btn_random.clicked.connect(self.random_voice)
        self.btn_random.setFixedSize(BW, BH)
        voice_btngrp.addWidget(self.btn_random)

        self.btn_play = QPushButton('Speak')
        self.btn_play.clicked.connect(self.speak)
        self.btn_play.setFixedSize(BW, BH)
        voice_btngrp.addWidget(self.btn_play)

        # LINE DISPLAY ===================
        self.line = Line()
        self.label = QLabel(self.line.display)
        lab_font = self.label.font()
        lab_font.setPixelSize(180)
        lab_font.setBold(True)
        lab_font.setFamily('Helvetica Extra Compressed')
        lab_font.setWordSpacing(40)
        self.label.setFont(lab_font)
        self.label.setWordWrap(True)
        self.label.setFixedHeight(700)
        self.label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.label)

        # TEXT CONTROL ================================
        textgrp = QHBoxLayout()
        textgrp.setAlignment(Qt.AlignHCenter)
        textgrp.setSpacing(50)
        layout.addLayout(textgrp)

        self.btn_generate = QPushButton('New Line')
        self.btn_generate.clicked.connect(self.new_line)
        self.btn_generate.setFixedSize(BW, BH)
        textgrp.addWidget(self.btn_generate)

        self.btn_log = QPushButton('Text Log: OFF')
        self.btn_log.setCheckable(True)
        self.btn_log.clicked.connect(self.toggle_log)
        self.btn_log.setFixedSize(BW, BH)
        textgrp.addWidget(self.btn_log)

    def new_line(self):
        self.line = Line()
        self.label.setText(self.line.display)
        if self.log_on:
            with open(self.log_file, 'a') as f:
                f.write(self.line.text + '\n')

    def toggle_log(self, checked):
        if not self.log_file:
            self.log_file = QFileDialog.getSaveFileName(
                self, directory=str(Path.home()))[0]
        self.log_on = checked
        if checked:
            self.btn_log.setText('Text Log: ON')
        else:
            self.btn_log.setText('Text Log: OFF')

    def set_lang(self, t):
        lang_index = list(LANGUAGES.values()).index(t)
        self.language = list(LANGUAGES)[lang_index]

    def set_voice(self, t):
        self.voice = t

    def set_pitch(self, n):
        self.pitch = n

    def set_speed(self, n):
        self.speed = n

    def set_gap(self, n):
        self.gap = n

    def set_amplitude(self, n):
        self.amplitude = n

    def random_voice(self):
        self.language = random.choice(list(LANGUAGES))
        self.ctl_lang.setCurrentText(LANGUAGES[self.language])
        self.voice = random.choice(VOICES)
        self.ctl_voice.setCurrentText(self.voice)
        self.pitch = random.randint(0, 99)
        self.ctl_pitch.setValue(self.pitch)
        self.speed = random.randint(25, 250)
        self.ctl_speed.setValue(self.speed)
        self.gap = random.randint(1, 40)
        self.ctl_gap.setValue(self.gap)

    def speak(self):
        espeak(f"[[{self.line}]]",
               language=self.language,
               voice=self.voice,
               pitch=self.pitch,
               speed=self.speed,
               gap=self.gap,
               amplitude=self.amplitude)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
