"""
Class for picking question purposes.
The picking strategy is - the more a question was answered correctly, the less changes it'll be picked.
"""
from enum import Enum
import random

from vocabulary.card import Card

TRAINING_MODE = 80


class Mode(Enum):
    REGULAR = 'regular'
    TRAINING = 'training'


class CardPicker:
    def __init__(self, cards: list, mode: Mode):
        self.weights = list()
        self.mode = mode
        self._initiate_weights(cards)

    def _initiate_weights(self, cards: list):
        for c in cards:
            card = Card(**c)
            weight = 100 - card.success_percent
            if self.mode == Mode.TRAINING and card.success_percent > TRAINING_MODE:
                weight = 0

            self.weights.append(weight)

    def pick_index(self):
        return random.choices(range(len(self.weights)), self.weights, k=1)[0]
