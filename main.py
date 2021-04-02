from dataclasses import dataclass, asdict
from enum import Enum
import json
import random
import re
import sys
import time
import platform
from enum import Enum

DB_PATH = r'C:\Windows\SysWOW64\Scripts\db.json'
HEBREW_REGEX = re.compile("^[\u0590-\u05fe ]+$")
IS_COLORING_ENABLED = False


class ColorText(Enum):
    RESET = "\033[0m"

    BOLD = "\033[1m"

    GRAY = "\x1b[1;30;40m"
    RED = "\033[1;31m"
    GREEN = "\033[1;32m"
    YELLOW = "\x1b[1;33;40m"
    BLUE = "\x1b[1;34;40m"
    PURPLE = "\x1b[1;35;40m"
    LIGHT_YELLOW = "\x1b[1;36;40m"
    WHITE = "\033[37m"


def _enable_coloring_in_windows_10():
    global IS_COLORING_ENABLED
    if not IS_COLORING_ENABLED and platform.system() == 'Windows' and platform.win32_ver()[0] == '10':
        # Enable coloring in windows 10
        import ctypes
        kernel32 = ctypes.WinDLL('kernel32')
        std_handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(std_handle, ctypes.byref(mode))
        mode.value |= 4
        kernel32.SetConsoleMode(std_handle, mode)

    IS_COLORING_ENABLED = True


def print_colorful_log(message: str, color: ColorText = ColorText.WHITE, bold: bool = False) -> None:
    _enable_coloring_in_windows_10()

    text = f"{color.value}{message}{ColorText.RESET.value}"
    if bold:
        text = f"{ColorText.BOLD.value}{text}{ColorText.RESET.value}"
    print(text)


def is_hebrew(string) -> bool:
    return bool(HEBREW_REGEX.match(string))


def wait_for_exit():
    input("\nEnter any key to exit...")


class Action(Enum):
    ANSWER = 'answer'
    ADD = 'add'
    STATS = 'stats'


@dataclass
class Question:
    question: str
    answer: str
    repeats: int = 0
    correct_repeats: int = 0

    def get_question(self) -> str:
        if is_hebrew(self.question):
            return self.question[::-1]

        return self.question

    def get_answer(self) -> str:
        if is_hebrew(self.answer):
            return self.answer[::-1]

        return self.answer

    def perform_answer(self) -> bool:
        self.repeats += 1

        response = ""

        while response == "":  # To avoid oopsies
            response = input(f"Question: {self.get_question()}\nAnswer: ")

        if response.strip() == self.answer.strip():
            print_colorful_log("You're correct!", color=ColorText.GREEN)
            self.correct_repeats += 1
            return True

        print_colorful_log(f"You're wrong! :(\nReal answer: {self.get_answer()}", color=ColorText.RED)
        return False

    def get_percent(self) -> str:
        if self.repeats == 0:
            return "0%"

        return f"{round(float(self.correct_repeats) / float(self.repeats) * 100, 2)}%"


class JsonDB:
    def __init__(self):
        self.db: List[dict] = None
        self._read()

    def _read(self):
        with open(DB_PATH, "r") as f:
            content = f.read()
        self.db = json.loads(content)

    def _write(self):
        content = json.dumps(self.db)
        with open(DB_PATH, "w") as f:
            f.write(content)

    def add_question(self, question: Question):
        self.db.append(asdict(question))
        self._write()

    def answer_question(self):
        if len(self.db) == 0:
            print_colorful_log("DB is empty!", color=ColorText.YELLOW)
            return

        random_index = random.randint(1, len(self.db))
        question = self.db[random_index - 1]

        q = Question(**question)
        q.perform_answer()

        self.db[random_index - 1] = asdict(q)
        self._write()

    def print_stats(self):
        if len(self.db) == 0:
            print_colorful_log("DB is empty!", color=ColorText.YELLOW)
            return

        from prettytable import PrettyTable
        t = PrettyTable(['Question', 'Answer', 'Tries', 'Correct', 'Percent'])
        for instance in self.db:
            q = Question(**instance)
            t.add_row([q.get_question(), q.get_answer(), q.repeats, q.correct_repeats, q.get_percent()])

        print(t)


if __name__ == '__main__':
    try:
        action = sys.argv[1]
        action = Action(action.strip())
    except IndexError:
        action = Action.ANSWER
    except:
        print_colorful_log("Unsupported action!", color=ColorText.RED)
        exit(1)

    db = JsonDB()

    if action == Action.ANSWER:
        db.answer_question()
    elif action == Action.ADD:
        question = input("Enter question: ")
        answer = input("Enter answer: ")
        db.add_question(Question(question=question, answer=answer))
    elif action == Action.STATS:
        db.print_stats()
    else:
        print_colorful_log("Unsupported action!", color=ColorText.RED)
        exit(1)

    wait_for_exit()
