from datetime import datetime, timedelta
import sys
from dataclasses import dataclass, asdict, field
from typing import Optional, List
from enum import Enum
import json
import random
import re
import sys
import time
import platform
import math
from enum import Enum

DB_PATH = r'C:\Windows\SysWOW64\Scripts\db.json'
HEBREW_REGEX = re.compile("^[\u0590-\u05fe ]+$")
IS_COLORING_ENABLED = False
SUCCESS_RATE = 80
DEFAULT_QUESTIONS_AMOUNT = 1
HINT_RATIO = 0.5


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


def get_colorful_test(message: str, color: ColorText = ColorText.WHITE, bold: bool = False) -> str:
    _enable_coloring_in_windows_10()

    text = f"{color.value}{message}{ColorText.RESET.value}"
    if bold:
        text = f"{ColorText.BOLD.value}{text}{ColorText.RESET.value}"

    return text


def print_colorful_log(message: str, color: ColorText = ColorText.WHITE, bold: bool = False) -> None:
    print(get_colorful_test(message, color, bold))


def is_hebrew(string) -> bool:
    return bool(HEBREW_REGEX.match(string))


def wait_for_exit():
    input("\nEnter any key to exit...")
    sys.exit(0)


class Action(Enum):
    ANSWER = 'answer'
    ADD = 'add'
    REMOVE = 'remove'
    STATS = 'stats'


@dataclass
class Question:
    question: str
    answer: str
    repeats: int = 0
    correct_repeats: int = 0
    last_wrong_answer_time: Optional[datetime] = None
    last_appearance_time: datetime = datetime.now()

    def __post_init__(self):
        if isinstance(self.last_wrong_answer_time, str):
            self.last_wrong_answer_time = datetime.strptime(self.last_wrong_answer_time, "%Y-%m-%d %H:%M:%S.%f")

        if isinstance(self.last_appearance_time, str):
            self.last_appearance_time = datetime.strptime(self.last_appearance_time, "%Y-%m-%d %H:%M:%S.%f")

    def get_question(self) -> str:
        if is_hebrew(self.question):
            return self.question[::-1]

        return self.question

    def get_answer(self) -> str:
        if is_hebrew(self.answer):
            return self.answer[::-1]

        return self.answer

    def get_hint(self) -> str:
        length = len(self.answer)
        words_hint = math.ceil(length * HINT_RATIO)
        hint_letters = random.sample(range(length), words_hint)

        a = ''
        for i, l in enumerate(self.answer):
            a += '_' if i in hint_letters else l

        return a

    def perform_answer(self) -> bool:
        self.repeats += 1
        hint = False
        self.last_appearance_time = datetime.now()

        response = ""

        while response == "":  # To avoid oopsies
            print_colorful_log(f'Question: {self.get_question()}', bold=True)
            response = InputInterface.input("Answer [? for hint]: ")

        response = response.strip().lower()

        if response == "?":
            print_colorful_log(f"Hint: {self.get_hint()}", color=ColorText.YELLOW)
            hint = True

            while response == "":  # To avoid oopsies
                print_colorful_log(f'Question: {self.get_question()}', bold=True)
            response = InputInterface.input("Answer: ")

        response = response.strip().lower()

        if response == self.answer.strip().lower():
            print_colorful_log("You're correct!", color=ColorText.GREEN)
            if not hint:
                self.correct_repeats += 1
            else:
                print_colorful_log("You've used an hint, so this answer won't count as a correct answer!", color=ColorText.YELLOW)
            return True

        print_colorful_log(f"You're wrong! :(\nReal answer: {self.get_answer()}", color=ColorText.RED)
        self.last_wrong_answer_time = datetime.now()
        return False

    @property
    def success_percent(self) -> float:
        if self.repeats == 0:
            return 0

        return round(float(self.correct_repeats) / float(self.repeats) * 100, 2)

    @property
    def was_answered_wrong_lately(self) -> bool:
        if not self.last_wrong_answer_time:
            return False

        return datetime.now() < self.last_wrong_answer_time + timedelta(weeks=1)

    @property
    def last_appearance_date(self):
        return str(self.last_appearance_time)[:10]


class JsonDB:
    def __init__(self):
        self.db: List[dict] = []
        self._read()

    def _read(self):
        with open(DB_PATH, "r") as f:
            content = f.read()
        self.db = json.loads(content)

    def _write(self):
        content = json.dumps(self.db, default=str)
        with open(DB_PATH, "w") as f:
            f.write(content)

    @classmethod
    def _translate_word(cls, word: str) -> str:
        from googletrans import Translator
        return Translator().translate(word, src='he').text

    def add_question(self):
        question = InputInterface.input("Enter question: ")

        answer = self._translate_word(question)
        res = ''

        while res not in ['n', 'y']:
            res = InputInterface.input_options(f"Does '{answer}' is the answer? [y/n] ", ['y', 'n'])

        if res == 'n':
            answer = InputInterface.input("Enter answer: ")

        question = Question(question=question, answer=answer)

        self.db.append(asdict(question))
        self._write()
        print_colorful_log("Question added successfully!", color=ColorText.GREEN)

    def answer_question(self, amount: int):
        if len(self.db) == 0:
            print_colorful_log("DB is empty!", color=ColorText.YELLOW)
            return

        for _ in range(amount):
            random_index = random.randint(1, len(self.db))
            question = self.db[random_index - 1]

            q = Question(**question)
            q.perform_answer()
            self.db[random_index - 1] = asdict(q)

        self._write()

    def remove_question(self):
        question_id = int(InputInterface.input("Enter question id to remove: "))
        self.db.pop(question_id)
        self._write()
        print_colorful_log("Question removed successfully!", color=ColorText.GREEN)

    def print_stats(self):
        if len(self.db) == 0:
            print_colorful_log("DB is empty!", color=ColorText.YELLOW)
            return

        from prettytable import PrettyTable
        t = PrettyTable(['ID', 'Question', 'Answer', 'Tries', 'Correct', 'Percent', 'Success Lately', 'Last answered'])
        for i, instance in enumerate(self.db):
            q = Question(**instance)

            success_color = ColorText.GREEN if not q.was_answered_wrong_lately else ColorText.RED
            was_answered_wrong_lately = get_colorful_test(str(not q.was_answered_wrong_lately), success_color)

            success_color = ColorText.GREEN if q.success_percent > SUCCESS_RATE else ColorText.RED
            success_percent_colored = get_colorful_test(f'{q.success_percent}%', success_color)

            t.add_row([i, q.get_question(), q.get_answer(), q.repeats, q.correct_repeats, success_percent_colored, was_answered_wrong_lately, q.last_appearance_date])

        print(t)
        total_questions = sum(x['repeats'] for x in self.db)
        total_correct_answer = sum(x['correct_repeats'] for x in self.db)
        if total_questions == 0:
            success_color = 0
        else:
            success_rate = round(float(total_correct_answer) / float(total_questions) * 100, 2)

        print(f"Total: {total_correct_answer}/{total_questions} (Success rate: {success_rate}%)")


def get_question_amounts() -> int:
    if len(sys.argv) != 4 or sys.argv[2] != "-n" or not sys.argv[3].isdigit():
        return DEFAULT_QUESTIONS_AMOUNT

    return int(sys.argv[3])


if __name__ == '__main__':
    try:
        action = sys.argv[1]
        action = Action(action.strip())
    except IndexError:
        action = Action.ANSWER
    except:
        print_colorful_log("Unsupported action!", color=ColorText.RED)
        sys.exit(1)

    db = JsonDB()

    if action == Action.ANSWER:
        amount = get_question_amounts()
        db.answer_question(amount=amount)
    elif action == Action.ADD:
        db.add_question()
    elif action == Action.STATS:
        db.print_stats()
        sys.exit(0)
    elif action == Action.REMOVE:
        db.remove_question()
        sys.exit(0)
    else:
        print_colorful_log("Unsupported action!", color=ColorText.RED)
        sys.exit(1)

    wait_for_exit()
