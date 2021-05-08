"""
Class for picking question purposes.
The picking strategy is - the more a question was answered correctly, the less changes it'll be picked.
"""
import random

from vocabulary.card import Card


class CardPicker:
    def __init__(self, cards: list):
        self.weights = list()
        self._initiate_weights(cards)

    def _initiate_weights(self, cards: list):
        self.weights = [100 - Card(**c).success_percent for c in cards]

    @property
    def pick_index(self):
        return random.choices(range(len(self.weights)), self.weights, k=1)[0]
