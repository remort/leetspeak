import logging
import re
import typing as t

from config import SERVICE_NAME
from normalizer import Normalizer
from objects import HEX_ALPHABET, SUBS, Replacement, Token, Word

log = logging.getLogger(f'{SERVICE_NAME}.{__name__}')
log.setLevel(logging.INFO)


class WordConverter:
    def __init__(self):
        self.__vocab: t.List[Replacement] = self.__make_vocab()
        self.__normalizer: Normalizer = Normalizer(self.__vocab)

        self.__string: str = ''
        self.__word: Word = Word()
        self.__normalized_word: Word = Word()

    def process(self, string: str) -> t.Tuple[Word, Word]:
        self.__string = string.strip().upper()
        self.__word = Word()
        self.__normalized_word = Word()
        self.__process()

        return self.__word, self.__normalized_word

    @staticmethod
    def __make_vocab() -> t.List[Replacement]:
        replacement_vocabulary = \
            [Replacement(old_chars=old, new_chars=new) for old, new in SUBS] +\
            [Replacement(old_chars=char, new_chars=char) for char in HEX_ALPHABET]
        return replacement_vocabulary

    def __replace(self) -> None:
        for sub in self.__vocab:
            for match in re.finditer(sub.old_chars, self.__string):
                start_pos = match.start()

                if start_pos in self.__word.positions:
                    log.info(
                        'Found replacement "%s" in pos %s which is already processed. Skip it.',
                        sub.old_chars,
                        start_pos,
                    )
                    continue

                log.info('Found new replacement: "%s"', sub.old_chars)
                token = Token(start=start_pos, end=start_pos + len(sub.old_chars), replacement=sub)
                self.__word.tokens.append(token)
                self.__word.positions.update({pos for pos in range(token.start, token.end)})

    def __process(self) -> None:
        log.info('Start trans1ee7erating word "%s".', self.__string)
        self.__replace()

        if len(self.__word.positions) != len(self.__string):
            log.info('Unable to convert word "%s".', self.__string)
            raise ValueError()

        self.__word.tokens.sort(key=lambda token: token.start)
        self.__normalized_word = Word(
            tokens=self.__word.tokens,
            char_count=self.__word.char_count,
            positions=self.__word.positions,
        )
        self.__normalized_word = self.__normalizer.normalize(self.__normalized_word)
