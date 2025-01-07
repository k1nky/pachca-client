from typing import Dict


def validate_button(func):
    def inner(*args, **kwargs):
        if len(args[0]) == 0:
            raise ValueError('text should be not empty')
        if len(args[1]) == 0:
            raise ValueError('value should be not empty')
        return func(*args, **kwargs)

    return inner


class Button:
    @staticmethod
    @validate_button
    def url(text: str, value: str) -> Dict:
        return {
            'text': text,
            'url': value
        }

    @staticmethod
    @validate_button
    def data(text: str, value: str) -> Dict:
        return {
            'text': text,
            'data': value
        }
