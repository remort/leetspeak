#!/usr/bin/env python3

import logging
import sys
import typing as t

from config import MAIN_LOGGING_LEVEL, SERVICE_NAME
from converter import WordConverter

log = logging.getLogger(SERVICE_NAME)

MAX_WORDS = 100
MAX_WORD_LEN = 20


def __get_words_from_incoming_arguments() -> t.List[str]:
    word_list = sys.argv[1:]
    resulting_list = []

    if len(word_list) > MAX_WORDS:
        log.warning('Words maximum limit %s exceeded.', MAX_WORDS)
        raise ValueError

    for incoming_word in word_list:
        if not incoming_word.isascii():
            log.warning('Word "%s" skipped. Only ASCII words, please.')
            continue

        if len(incoming_word) > MAX_WORD_LEN:
            log.warning('Word "%s" skipped. Maximum word length "%s" exceeded.', incoming_word, MAX_WORD_LEN)
            continue

        resulting_list.append(incoming_word)

    return resulting_list


def __setup_logging():
    formatter = logging.Formatter('%(levelname)s:%(name)s: %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(MAIN_LOGGING_LEVEL)
    ch.setFormatter(formatter)
    log.addHandler(ch)


if __name__ == '__main__':
    __setup_logging()

    words = None
    try:
        words = __get_words_from_incoming_arguments()
    except ValueError:
        exit(1)

    log.info('Incoming words: %s', words)
    tokenizer = WordConverter()

    output = ''
    for word in words:
        try:
            wrd, alt_wrd = tokenizer.process(word)
            word_output = f'{wrd} ' if (not alt_wrd or wrd == alt_wrd) else f'{wrd} ({alt_wrd}) '
            output += word_output
        except ValueError:
            output += f'(Error encoding word: {word}) '
    print(output)
