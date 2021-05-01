from dataclasses import asdict
from typing import List
import json

from googletrans import Translator
from prettytable import PrettyTable

from .args import InputInterface
from .bank import Bank
from .logging import print_colorful_log, ColorText, get_colorful_text
from .picker import QuestionPicker
from .question import Question


DB_PATH = r'C:\Windows\SysWOW64\Scripts\db.json'
SUCCESS_RATE = 80


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

    def add_topic(self):
        bank = Bank()
        topics = bank.get_topics()
        print_colorful_log(f"Available topics:\n {'n'.join(topics)}", color=ColorText.WHITE)

    def pick_question(self, picker: QuestionPicker):
        random_index = picker.pick_index
        question = self.db[random_index]

        return Question(**question), random_index

    def answer_question(self, amount: int):
        if len(self.db) == 0:
            print_colorful_log("DB is empty!", color=ColorText.YELLOW)
            return

        picker = QuestionPicker(self.db)
        for _ in range(amount):
            q, index = self.pick_question(picker)
            q.perform_answer()
            self.db[index] = asdict(q)

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

        t = PrettyTable(['ID', 'Question', 'Answer', 'Tries', 'Correct', 'Percent', 'Success Lately', 'Last answered'])
        for i, instance in enumerate(self.db):
            q = Question(**instance)

            success_color = ColorText.GREEN if not q.was_answered_wrong_lately else ColorText.RED
            was_answered_wrong_lately = get_colorful_text(str(not q.was_answered_wrong_lately), success_color)

            success_color = ColorText.GREEN if q.success_percent > SUCCESS_RATE else ColorText.RED
            success_percent_colored = get_colorful_text(f'{q.success_percent}%', success_color)

            t.add_row([i, q.get_question(), q.get_answer(), q.repeats, q.correct_repeats, success_percent_colored, was_answered_wrong_lately, q.last_appearance_date])

        print(t)
        total_questions = sum(x['repeats'] for x in self.db)
        total_correct_answer = sum(x['correct_repeats'] for x in self.db)

        success_rate = 0 if total_questions == 0 else round(float(total_correct_answer) / float(total_questions) * 100, 2)

        print(f"Total: {total_correct_answer}/{total_questions} (Success rate: {success_rate}%)")
