from enum import Enum


class StrEnum(str, Enum):
    ...


class Platform(StrEnum):
    PC = 'pc'
    PS2 = 'ps2'
    XBOX = 'xbox'

    def __str__(self):
        return self.value


class Language(StrEnum):
    ENGLISH = 'english'
    FRENCH = 'french'
    GERMAN = 'german'
    ITALIAN = 'italian'
    JAPANESE = 'japanese'
    SPANISH = 'spanish'
    UK_ENGLISH = 'uk'

    def __str__(self):
        return self.value


MUNGE_ALL = 'EVERYTHING'
ALL_PLATFORMS = (Platform.PC, Platform.PS2, Platform.XBOX)
ALL_LANGUAGES = (Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.ITALIAN, Language.JAPANESE,
                 Language.SPANISH, Language.UK_ENGLISH)
