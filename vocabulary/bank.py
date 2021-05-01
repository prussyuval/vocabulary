from typing import List, Dict

import requests


class UnrecognizedTopic(Exception):
    pass


class Bank:
    BANK_URL = "https://raw.githubusercontent.com/prussyuval/vocabulary/main/vocabulary/bank.json"

    def __init__(self):
        self.data = requests.get(self.BANK_URL).json()

    def get_topics(self) -> List[str]:
        return [
            topic['topic']
            for topic in self.data
        ]

    def get_words(self, topic_name: str) -> Dict[str, str]:
        for topic in self.data:
            if topic['topic'] != topic_name:
                continue

            return topic['words']

        raise UnrecognizedTopic()
