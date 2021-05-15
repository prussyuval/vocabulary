from dataclasses import asdict
from typing import List
import json

from googletrans import Translator
from prettytable import PrettyTable

from .args import InputInterface
from .bank import Bank
from .logging import print_colorful_log, ColorText
from .picker import CardPicker, Mode
from .card import Card
from .console import safe_print
from vocabulary.stats import StatsManager


DB_PATH = r'C:\Windows\SysWOW64\Scripts\db.json'
NEW_LINE = '\n'


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

        question = Card(question=question, answer=answer)

        self.db.append(asdict(question))
        self._write()
        print_colorful_log("Card added successfully!", color=ColorText.GREEN)

    def add_topic(self):
        bank = Bank()
        topics = bank.get_topics()
        print_colorful_log("Available topics:", color=ColorText.WHITE)
        for i, t in enumerate(topics, start=1):
            print_colorful_log(f"[{i}] {safe_print(t)}", color=ColorText.WHITE)
        topic_number = InputInterface.input_options("Select topic number: ", options=[str(x + 1)
                                                                                      for x in range(len(topics))])

        words = bank.get_words(topics[int(topic_number) - 1])

        print_colorful_log("Pushed words:", color=ColorText.WHITE)
        for question, answer in words.items():
            print_colorful_log(f"{safe_print(question)} => {answer}", color=ColorText.WHITE)

        res = InputInterface.input_options(f"DO you approve adding those words to your vocabulary? [y/n] ", ['y', 'n'])
        if res == 'n':
            print_colorful_log("Words skipped successfully", color=ColorText.GREEN)
            return

        for question, answer in words.items():
            question = Card(question=question, answer=answer)
            self.db.append(asdict(question))
        self._write()
        print_colorful_log("Words added successfully", color=ColorText.GREEN)

    def pick_question(self, picker: CardPicker):
        random_index = picker.pick_index()
        question = self.db[random_index]

        return Card(**question), random_index

    def answer_question(self, amount: int, mode: Mode):
        if len(self.db) == 0:
            print_colorful_log("DB is empty!", color=ColorText.YELLOW)
            return

        picker = CardPicker(self.db, mode)
        for _ in range(amount):
            q, index = self.pick_question(picker)
            q.perform_answer()
            self.db[index] = asdict(q)

        self._write()

    def remove_question(self):
        question_id = int(InputInterface.input("Enter question id to remove: "))
        self.db.pop(question_id)
        self._write()
        print_colorful_log("Card removed successfully!", color=ColorText.GREEN)

    def print_stats(self):
        StatsManager.print_stats(self.db)
