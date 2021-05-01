import re


HEBREW_REGEX = re.compile("^[\u0590-\u05fe ]+$")


def _is_hebrew(string: str) -> bool:
    return bool(HEBREW_REGEX.match(string))


def safe_print(string: str) -> str:
    if _is_hebrew(string):
        return string[::-1]

    return string
