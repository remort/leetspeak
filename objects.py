import typing as t
from dataclasses import dataclass, field

HEX_ALPHABET = 'ABCDEF0123456789'
SUBS = [
    ('FOR', '4'),
    ('FOUR', '4'),
    ('TO', '2'),
    ('ATE', '8'),
    ('TEN', '10'),
    ('ILL', '177'),
    ('CK', 'CC'),
    ('NIGH', '9'),
    ('B', '8'),
    ('G', '9'),
    ('L', '1'),
    ('I', '1'),
    ('O', '0'),
    ('S', '5'),
    ('T', '7'),
    ('R', '12'),
    ('N', '17'),
    ('Z', '2')
]


@dataclass
class Replacement:
    old_chars: str
    new_chars: str


@dataclass
class Token:
    start: int
    end: int
    replacement: Replacement


@dataclass
class Word:
    tokens: t.List[Token] = field(default_factory=list)
    char_count: int = 0
    positions: t.Set = field(default_factory=set)

    def __as_string(self):
        return ''.join((token.replacement.new_chars for token in self.tokens))

    def __str__(self):
        return self.__as_string()

    def __repr__(self):
        return self.__as_string()
