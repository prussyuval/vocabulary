from typing import List

from prettytable import PrettyTable

from vocabulary.card import Card
from vocabulary.logging import print_colorful_log, ColorText, get_colorful_text


SUCCESS_RATE = 80


class StatsManager:
    @staticmethod
    def print_success_rate(cards: List[Card]):
        total_questions = sum(x.repeats for x in cards)
        total_correct_answer = sum(x.correct_repeats for x in cards)

        success_rate = 0 if total_questions == 0 else round(float(total_correct_answer) / float(total_questions) * 100, 2)

        print(f"Total: {total_correct_answer}/{total_questions} (Success rate: {success_rate}%)")

    @classmethod
    def print_stats(cls, cards: List[dict]) -> None:
        cards = [Card(**c) for c in cards]

        if len(cards) == 0:
            print_colorful_log("DB is empty!", color=ColorText.YELLOW)
            return

        t = PrettyTable(['ID', 'Question', 'Answer', 'Tries', 'Correct', 'Percent', 'Success Lately', 'Last answered'])
        for i, c in enumerate(cards):
            success_color = ColorText.GREEN if not c.was_answered_wrong_lately else ColorText.RED
            was_answered_wrong_lately = get_colorful_text(str(not c.was_answered_wrong_lately), success_color)

            success_color = ColorText.GREEN if c.success_percent > SUCCESS_RATE else ColorText.RED
            success_percent_colored = get_colorful_text(f'{c.success_percent}%', success_color)

            t.add_row([i, c.get_question(), c.get_answer(), c.repeats, c.correct_repeats, success_percent_colored, was_answered_wrong_lately, c.last_appearance_date])

        print(t)
        cls.print_success_rate(cards)