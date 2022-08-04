import sys
import random
from pathlib import Path
from tempfile import gettempdir
from typing import Union

from pySpeakNG import speak as espeak
from pySpeakNG import LANGUAGES, VOICES
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

HERE = Path(__file__).parent.resolve()
TMP = Path(gettempdir())

CLAB = {'p': 'p', 'b': 'b', 'f': 'f', 'v': 'v', }
CDENT = {'θ': 'T', 'ð': 'D', }
CALV = {'t': 't', 'd': 'd', 's': 's', 'z': 'z', }
CPALV = {'tʃ': 'tS', 'dʒ': 'dZ', 'ʃ': 'S', 'ʒ': 'Z', }
CVEGL = {'k': 'k', 'g': 'g', 'x': 'x', 'h': 'h', }
CNAS = {'m': 'm', 'n': 'n', 'ŋ': 'N', }
CAPP = {'l': 'l', 'ɹ': 'r', 'j': 'j', 'w': 'w', }
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
