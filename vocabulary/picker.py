"""
Class for picking question purposes.
The picking strategy is - the more a question was answered correctly, the less changes it'll be picked.
"""
import random

from vocabulary.question import Question


class QuestionPicker:
    def __init__(self, questions: list):
        self.weights = list()
        self._initiate_weights(questions)

    def _initiate_weights(self, questions: list):
        self.weights = [100 - Question(**q).success_percent for q in questions]

    @property
    def pick_index(self):
        return random.choices(range(len(self.weights)), self.weights, k=1)[0]
