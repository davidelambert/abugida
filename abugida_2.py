import sys
import random
import uuid
from pathlib import Path

import gtts
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
ACCENT = {
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
        self.btn_generate.clicked.connect(self.generate)
        btn_font = self.btn_generate.font()
        btn_font.setPixelSize(40)
        self.btn_generate.setFont(btn_font)
        self.btn_generate.setFixedSize(BSIZE, BSIZE)
        btn_maingrp.addWidget(self.btn_generate)

        self.btn_play = QPushButton(u'\u25B6')
        self.btn_play.clicked.connect(self.play)
        self.btn_play.setFont(btn_font)
        self.btn_play.setFixedSize(BSIZE, BSIZE)
        btn_maingrp.addWidget(self.btn_play)

        self.btn_log = QPushButton(u'\u25CF')
        self.btn_log.setCheckable(True)
        self.btn_log.clicked.connect(self.toggle_log)
        self.btn_log.setFont(btn_font)
        self.btn_log.setFixedSize(BSIZE, BSIZE)
        btn_maingrp.addWidget(self.btn_log)

    def generate(self):
        self.line = Line()
        self.label.setText(self.line.display)
        if self.log_on:
            with open(self.log_file, 'a') as f:
                f.write(self.line.text + '\n')

    def play(self):
        text = self.line.text

        langs = []
        for lang in random.choices(LANGS, k=3):
            if lang in list(ACCENT):
                langs.append((lang, random.choice(ACCENT[lang])))
            else:
                langs.append((lang, 'com'))

        slow = random.choice([True, False])

        mp3_files = []
        for i in range(len(langs)):
            name = str(uuid.uuid4()) + '.mp3'
            mp3_files.append(TMP/name)

        for i in range(len(mp3_files)):
            try:
                tts = gtts.gTTS(
                    text=text,
                    lang=langs[i][0],
                    tld=langs[i][1],
                    slow=slow
                )
            except gtts.gTTSError:
                tts = gtts.gTTS(
                    text=text,
                    lang=langs[i][0],
                    tld=langs[i][1],
                    slow=slow
                )
            tts.save(mp3_files[i])

        audio = [AudioSegment.from_mp3(str(f)) for f in mp3_files]
        audio.sort(key=lambda x: len(x), reverse=True)

        mixed = audio[0]
        for i in range(1, len(audio)):
            mixed = mixed.overlay(audio[i])
        mix_name = str(uuid.uuid4()) + '.mp3'
        mixed.export(TMP/mix_name, format='wav')
        self.sound_file = TMP/mix_name

        playsound(self.sound_file)

    def toggle_log(self, checked):
        if not self.log_file:
            self.log_file = QFileDialog.getSaveFileName(
                self, directory=str(Path.home()))[0]
        self.log_on = checked


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
