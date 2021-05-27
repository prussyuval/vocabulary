from enum import Enum


class Action(Enum):
    ANSWER = 'answer'
    ADD = 'add'
    ADD_TOPIC = 'add_topic'
    REMOVE = 'remove'
    ARCHIVE = 'archive'
    UNARCHIVE = 'unarchive'
    STATS = 'stats'

    @property
    def is_waitable_actions(self) -> bool:
        return self in [self.ANSWER, self.ADD]
