import sys
import random
import time
from pathlib import Path

import gtts
import pyttsx3
from pedalboard import (Pedalboard,
                        Distortion,
                        Chorus,
                        Delay,
                        PitchShift,
                        Limiter)
from pedalboard.io import AudioFile
from pydub import AudioSegment
from playsound import playsound

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *


HERE = Path(__file__).parent.resolve()
TMP = HERE/'tmp/'
if not TMP.exists():
    TMP.mkdir()

VOWELS = ('A', 'U', 'I', 'Ai', 'Au')
CONSONANTS = ('B', 'G', 'D')
SYLLABLES = [c + v.lower() for c in CONSONANTS for v in VOWELS] + list(VOWELS)
MAX_SYL = 4

LANGS = list(gtts.lang.tts_langs())
ACCENTS = {
    'en': ['com.au', 'co.uk', 'com', 'ca', 'co.in', 'ie', 'co.za'],
    'fr': ['ca', 'fr'],
    'pt': ['com.br', 'pt'],
    'es': ['com', 'com.mx', 'es'],
}


class Line:
    def __init__(self):
        self.display = ''

        max_len = 30
        n_words = random.randint(3, 5)

        i = 0
        while i < n_words - 1:  # spaces after all but last word
            self.display += self.word()
            self.display += ' '
            i += 1
        self.display += self.word()
        i += 1

        while len(self.display) > max_len:
            self.display = self.display[:self.display.rfind('-')]

        self.text = self.display.replace('-', '').capitalize()

    @classmethod
    def word(cls):
        n_syl = random.randint(1, MAX_SYL)
        text = ''
        i = 0
        while i < n_syl - 1:  # all but last syllable
            text = text + random.choice(SYLLABLES) + '-'
            i += 1
        text = text + random.choice(SYLLABLES)  # no hyphen after last syllable
        return text

    def __repr__(self):
        return self.display

    def __str__(self):
        return self.text


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abugida 2: Vogon Poetry")
        self.showMaximized()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        BSIZE = 80
        self.log_on = False
        self.log_file = None
        self.sound_file = None

        # LINE DISPLAY ===================
        self.line = Line()
        self.label = QLabel(self.line.display)
        lab_font = self.label.font()
        lab_font.setPixelSize(200)
        lab_font.setBold(True)
        lab_font.setFamily('Helvetica Ultra Compressed')
        lab_font.setWordSpacing(40)
        self.label.setFont(lab_font)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # BUTTONS ================================
        btn_maingrp = QHBoxLayout()
        btn_maingrp.setAlignment(Qt.AlignHCenter)
        btn_maingrp.setSpacing(50)
        layout.addLayout(btn_maingrp)

        self.btn_generate = QPushButton(u'\u21BB')  # cwise open circle arrow ↻
        self.btn_generate.clicked.connect(self.new_line)
        btn_font = self.btn_generate.font()
        btn_font.setPixelSize(40)
        self.btn_generate.setFont(btn_font)
        self.btn_generate.setFixedSize(BSIZE, BSIZE)
        btn_maingrp.addWidget(self.btn_generate)

        self.btn_play = QPushButton(u'\u25B6')
        self.btn_play.clicked.connect(self.gen_speech)
        self.btn_play.setFont(btn_font)
        self.btn_play.setFixedSize(BSIZE, BSIZE)
        btn_maingrp.addWidget(self.btn_play)

        self.btn_log = QPushButton(u'\u25CF')
        self.btn_log.setCheckable(True)
        self.btn_log.clicked.connect(self.toggle_log)
        self.btn_log.setFont(btn_font)
        self.btn_log.setFixedSize(BSIZE, BSIZE)
        btn_maingrp.addWidget(self.btn_log)

    def new_line(self):
        self.line = Line()
        self.label.setText(self.line.display)
        if self.log_on:
            with open(self.log_file, 'a') as f:
                f.write(self.line.text + '\n')

    def gen_speech(self):
        text = self.line.text
        self.sound_file = TMP/'tmp.mp3'
        lang = random.choice(LANGS)
        if lang in list(ACCENTS):
            tld = random.choice(ACCENTS[lang])
        else:
            tld = 'com'
        slow = random.choice([True, False])

        robot = random.choice([True, False])
        if robot:
            self.robot(self.line.text)
        else:
            try:
                self.tts(text, lang, tld, slow, filename=self.sound_file)
            except Exception as e:
                print(e)
                self.robot(self.line.text)

    @classmethod
    def tts(cls, text, lang, tld, slow, filename):
        output = gtts.gTTS(
            text=text,
            lang=lang,
            tld=tld,
            slow=slow
        )
        output.save(filename)
        playsound(filename)

    @classmethod
    def robot(cls, text):
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        voice = random.choice(voices)
        engine.setProperty('voice', voice.id)
        rate = random.randint(1, 150)
        engine.setProperty('rate', rate)
        engine.say(text)
        engine.runAndWait()

    def toggle_log(self, checked):
        if not self.log_file:
            self.log_file = QFileDialog.getSaveFileName(
                self, directory=str(Path.home()))[0]
        self.log_on = checked


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
