from typing import List

DEFAULT_QUESTIONS_AMOUNT = 1


class InputInterface:
    @classmethod
    def input_options(cls, text: str, options: List[str]) -> str:
        x = None
        while x not in options:
            x = input(text).strip()

        return x

    @classmethod
    def input(cls, text: str) -> str:
        x = ''
        while x == '':
            x = input(text).strip()

        return x
