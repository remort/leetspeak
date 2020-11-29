import logging
import typing as t

from config import SERVICE_NAME
from objects import Replacement, Token, Word

log = logging.getLogger(f'{SERVICE_NAME}.{__name__}')
log.setLevel(logging.INFO)


class Normalizer:
    """
    Finds if there are two equal multichar replacements goes one after another.
    If such pair found, try to re-encode first multichar replacement to single letter replacements.
    If 'forfours' was encoded to 445, it will be normalized to FOR45 by re-encoding first 'for' to FOR.
    """
    def __init__(self, vocab: t.List[Replacement]):
        self.__vocab = vocab

    def normalize(self, word: Word) -> Word:
        normalized_word = word
        normalized_word = self.__break_up_multi_char_duplicate_tokens(normalized_word)
        return normalized_word

    def __break_up_multi_char_duplicate_tokens(self, word: Word) -> Word:
        log.info('Start searching for duplicated tokens in word "%s".', word)
        word_tokens = []
        prev_token = None
        change_made = False

        for token in word.tokens:
            if not prev_token:
                prev_token = token
                word_tokens.append(token)
                continue

            log.info('Walking token "%s", previous token: "%s".', token, prev_token)
            if token.replacement.new_chars == prev_token.replacement.new_chars and \
                    len(token.replacement.old_chars) > 1 and \
                    not change_made:
                log.info('Duplicate multi-char token "%s" found.', token.replacement.old_chars)

                try:
                    simple_tokens = self.__split_up_complex_token(token)
                except ValueError:
                    log.info('Duplicate multi-char token broke up failed. Try to break up first token in pair.')
                    if len(prev_token.replacement.old_chars) == 1:
                        log.info(
                            'Unable to break up tokens pair "%s%s". Leave it as is, search next duplicates.',
                            prev_token.replacement.new_chars,
                            token.replacement.new_chars,
                        )
                        prev_token = token
                        word_tokens.append(token)
                        continue

                    try:
                        simple_tokens = self.__split_up_complex_token(prev_token)
                    except ValueError:
                        log.info(
                            'Unable to break up neither first nor second token in token pair duplicates "%s%s". '
                            'Leave it as is, search next duplicates.',
                            prev_token.replacement.new_chars,
                            token.replacement.new_chars,
                        )
                    else:
                        word_tokens.pop()
                        word_tokens.extend(simple_tokens)
                        change_made = True
                        log.info('First duplicate multi-char token in pair broke up to single char tokens.')
                    finally:
                        word_tokens.append(token)
                else:
                    word_tokens.extend(simple_tokens)
                    change_made = True
                    log.info('Duplicate multi-char token broke up to single char tokens.')

            else:
                word_tokens.append(token)

            prev_token = token

        log.info('Resulting tokens: %s', word_tokens)
        word.tokens = word_tokens
        if change_made:
            log.info('Duplicates found in word "%s", search them in this word again.', word)
            self.__break_up_multi_char_duplicate_tokens(word)

        log.info('All complex token duplicates changed to single char ones. Normalized word is %s.', word)
        return word

    def __split_up_complex_token(self, token: Token) -> t.List[Token]:
        single_char_tokens = []
        start = None
        end = None
        for char in token.replacement.old_chars:
            log.info(char)
            start = token.start if not start else start + 1
            end = token.start + 1 if not end else end + 1

            for sub in self.__vocab:
                if len(sub.old_chars) > 1:
                    continue

                if sub.old_chars == char:
                    replacement = Replacement(old_chars=char, new_chars=char)
                    simple_token = Token(start=start, end=end, replacement=replacement)
                    single_char_tokens.append(simple_token)
                    break
            else:
                log.info(
                    'Unable to break up duplicated token "%s" to single chars. Leave this duplicate in word.',
                    token.replacement.old_chars,
                )
                raise ValueError()

        if len(single_char_tokens) != len(token.replacement.old_chars):
            log.warning('Unable to parse complex token to single-char tokens.')
            raise ValueError()

        return single_char_tokens
