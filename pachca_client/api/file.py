import os
from typing import Dict

TYPE_FILE = 'file'
TYPE_IMAGE = 'image'


class File:
    def __init__(self, file_path: str, name: str = '', file_type: str = TYPE_FILE) -> None:
        self.name = name
        if self.name == '':
            self.name = os.path.basename(file_path)
        self.path = file_path
        self.type = file_type
        self.size = 0
        self.key = ''

    def as_dict(self) -> Dict:
        return {
            'key': self.key,
            'name': self.name,
            'file_type': self.type,
            'size': self.size
        }

    def get_size(self) -> int:
        return os.path.getsize(self.path)

    def prepare(self, key: str) -> None:
        self.key = key.replace('${filename}', self.name)
        self.size = self.get_size()
