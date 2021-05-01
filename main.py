import sys

from vocabulary.action import Action
from vocabulary.args import get_desired_action, get_desired_question_amounts
from vocabulary.db import JsonDB
from vocabulary.logging import print_colorful_log, ColorText


def wait_for_exit():
    input("\nEnter any key to exit...")
    sys.exit(0)


if __name__ == '__main__':
    action = get_desired_action()

    db = JsonDB()

    if action == Action.ANSWER:
        amount = get_desired_question_amounts()
        db.answer_question(amount=amount)
    elif action == Action.ADD:
        db.add_question()
    elif action == Action.ADD_TOPIC:
        db.add_topic()
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
