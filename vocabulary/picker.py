"""
Class for picking question purposes.
The picking strategy is - the more a question was answered correctly, the less changes it'll be picked.
"""
import random

from vocabulary.card import Card
from vocabulary.mode import Mode


class CardPicker:
    def __init__(self, cards: list, mode: Mode):
        self.weights = list()
        self.mode = mode
        self._initiate_weights(cards)

    def _initiate_weights(self, cards: list):
        max_repeats = max(c['repeats'] for c in cards)
        for c in cards:
            card = Card(**c)
            weight = card.get_weight(max_repeats, self.mode)
            self.weights.append(weight)

    def pick_index(self):
        return random.choices(range(len(self.weights)), self.weights, k=1)[0]
