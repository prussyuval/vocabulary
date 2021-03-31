from dataclasses import dataclass, asdict
from enum import Enum
import json
import random
import re
import sys

DB_PATH = r'C:\Windows\SysWOW64\Scripts\db.json'
HEBREW_REGEX = re.compile("^[\u0590-\u05fe ]+$")


def is_hebrew(string) -> bool:
    return bool(HEBREW_REGEX.match(string))


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

        response = input(f"Question: {self.get_question()}\nAnswer: ")
        if response.strip() == self.answer.strip():
            print("You're correct!")
            self.correct_repeats += 1
            return True

        print(f"You're wrong! :(\nReal answer: {self.get_answer()}")
        return False

    def get_percent(self) -> str:
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
            print("DB is empty!")
            return

        random_index = random.randint(1, len(self.db))
        question = self.db[random_index - 1]

        q = Question(**question)
        q.perform_answer()

        self.db[random_index - 1] = asdict(q)
        self._write()

    def print_stats(self):
        if len(self.db) == 0:
            print("DB is empty!")
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
        print("Unsupported action!")
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
        print("Unsupported action!")
