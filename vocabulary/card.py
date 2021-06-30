from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional
import random
import math

from .args import InputInterface
from .console import safe_print
from .logging import print_colorful_log, ColorText
from .mode import Mode

HINT_RATIO = 0.5
TRAINING_MODE = 80
SAFE_TEXT_CHARACTER_NUMBER = 20


@dataclass
class Card:
    question: str
    answer: str
    repeats: int = 0
    correct_repeats: int = 0
    last_wrong_answer_time: Optional[datetime] = None
    last_appearance_time: datetime = datetime.now()
    creation_time: datetime = datetime.now()
    is_archived: bool = False

    def __post_init__(self):
        if isinstance(self.last_wrong_answer_time, str):
            self.last_wrong_answer_time = datetime.strptime(self.last_wrong_answer_time, "%Y-%m-%d %H:%M:%S.%f")

        if isinstance(self.last_appearance_time, str):
            self.last_appearance_time = datetime.strptime(self.last_appearance_time, "%Y-%m-%d %H:%M:%S.%f")

        if isinstance(self.creation_time, str):
            self.creation_time = datetime.strptime(self.creation_time, "%Y-%m-%d %H:%M:%S.%f")

    def get_question(self, full_text: bool = True) -> str:
        text = safe_print(self.question)
        if not full_text:
            text = text[:SAFE_TEXT_CHARACTER_NUMBER]

        return text

    def get_answer(self) -> str:
        return safe_print(self.answer)

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
            print_colorful_log(f'Card: {self.get_question()}', bold=True)
            response = InputInterface.input("Answer [? for hint]: ")

        response = response.strip().lower()

        if response == "?":
            print_colorful_log(f"Hint: {self.get_hint()}", color=ColorText.YELLOW)
            hint = True

            while response == "":  # To avoid oopsies
                print_colorful_log(f'Card: {self.get_question()}', bold=True)
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

    def get_weight(self, max_repeats: int, mode: Mode) -> float:
        if self.is_archived:
            return 0

        if mode == Mode.TRAINING and self.success_percent > TRAINING_MODE:
            return 0

        return 100 - (self.success_percent * (self.repeats / max_repeats))

    @property
    def was_answered_wrong_lately(self) -> bool:
        if not self.last_wrong_answer_time:
            return False

        return datetime.now() < self.last_wrong_answer_time + timedelta(weeks=1)

    @property
    def last_appearance_date(self):
        return str(self.last_appearance_time)[:10]
