import argparse
import sys

from vocabulary.action import Action
from vocabulary.bank import UnrecognizedTopic
from vocabulary.db import JsonDB
from vocabulary.picker import Mode
from vocabulary.logging import print_colorful_log, ColorText


def wait_for_exit():
    input("\nEnter any key to exit...")
    sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('action', type=Action, choices=list(Action))
    parser.add_argument('-n', dest='amount', default=1, type=int,
                        help='amount of questions to answer (default: 1)')
    parser.add_argument('-m', dest='mode', type=Mode, default=Mode.REGULAR, choices=list(Mode),
                        help='answering mode type')
    args = parser.parse_args()

    db = JsonDB()

    action = args.action

    if action == Action.ANSWER:
        db.answer_question(amount=args.amount, mode=args.mode)
    elif action == Action.ADD:
        db.add_question()
    elif action == Action.ADD_TOPIC:
        try:
            db.add_topic()
        except UnrecognizedTopic:
            print_colorful_log("Unrecognized topic!", color=ColorText.RED)
    elif action == Action.STATS:
        db.print_stats()
        sys.exit(0)
    elif action == Action.REMOVE:
        db.remove_question()
        sys.exit(0)

    wait_for_exit()
