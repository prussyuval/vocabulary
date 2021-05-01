import sys
from typing import List

from .action import Action
from .logging import print_colorful_log, ColorText

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


def get_desired_question_amounts() -> int:
    if len(sys.argv) != 4 or sys.argv[2] != "-n" or not sys.argv[3].isdigit():
        return DEFAULT_QUESTIONS_AMOUNT

    return int(sys.argv[3])


def get_desired_action() -> Action:
    try:
        action = sys.argv[1]
        return Action(action.strip())
    except IndexError:
        return Action.ANSWER
    except:
        print_colorful_log("Unsupported action!", color=ColorText.RED)
        sys.exit(1)
