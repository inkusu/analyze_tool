import re

import spacy

from context.nlp.stopword import stop_words

URL = re.compile(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)")
ZERO_NUMBER = re.compile(r'[0-9]+')
ADJUST_MENTION = re.compile(r'@([A-Za-z0-9_]+)')
HASH_TAG = re.compile(r"#(\w+)")
# REMOVE_SYMBOL_Z = re.compile("[!-/:-@[-`{-~]")
REMOVE_SYMBOL_H = re.compile(r'[︰-＠]')


def nlp():
    nlp = spacy.load('ja_ginza')
    for w in stop_words:
        nlp.vocab[w].is_stop = True

    return nlp


class CleanText:

    def __init__(self, text):
        self._text = text

    def to_lower(self):
        """全角から半角にしてから、小文字化"""
        self._text = self._text.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})).lower()

        return self

    def to_adjust_line_code(self):
        self._text = self._text.replace("\n", " ")
        return self

    def to_remove_url(self):
        self._text = re.sub(URL, " ", self._text)
        return self

    def to_adjust_zero_number(self):
        self._text = re.sub(ZERO_NUMBER, "0", self._text)
        return self

    def to_adjust_mention(self):
        self._text = re.sub(ADJUST_MENTION, " ", self._text)
        return self

    def to_remove_hash_tag(self):
        self._text = re.sub(HASH_TAG, " ", self._text)
        return self

    def to_remove_symbol(self):
        self._text = re.sub(REMOVE_SYMBOL_H, " ", self._text)
        self._text = self._text.replace("RT ", " ").replace("rt ", " ").replace(":", " ").replace("…", " ")
        # self._text = re.sub(REMOVE_SYMBOL_Z, "", self._text)

        return self

    @property
    def text(self):
        return self._text.strip(" ")


if __name__ == '__main__':
    # 簡易テストコード
    ct = CleanText("ASDASD @ASDASD")
    assert "asdasd @asdasd" == ct.to_lower().text

    ct = CleanText("ASDASD\n@ASDASD")
    assert "ASDASD @ASDASD" == ct.to_adjust_line_code().text

    ct = CleanText("ASDASD @ASDASD https://asdasdsada.com http://asdasdsad.com")
    assert "ASDASD @ASDASD" == ct.to_remove_url().text

    ct = CleanText("A123SDASD 2343@ASD00ASD 9999")
    assert "A0SDASD 0@ASD0ASD 0" == ct.to_adjust_zero_number().text

    ct = CleanText("ASDASD @ASDASD 0")
    assert "ASDASD  0" == ct.to_adjust_mention().text

    ct = CleanText("asdad3あああああ-4923rl';''5o-43[52'f~!#!@$#^**^&(dsl;f @ASDASD 0")
    assert "asdad3あああああ4923rl5o4352fdslf ASDASD 0" == ct.to_remove_symbol().text

