from datetime import datetime
from typing import Any


class Cache:
    def __init__(self, ttl: int = 60) -> None:
        if ttl == 0:
            raise ValueError("ttl should be greater 0")
        self.cache = {}
        self.ttl = {}
        self.max_ttl = ttl

    def update(self, scope: str, value: Any) -> None:
        self.ttl[scope] = datetime.now().timestamp() + self.max_ttl
        self.cache[scope] = value

    def get(self, scope: str) -> Any:
        if scope not in self.cache:
            return None
        if self.ttl[scope] < datetime.now().timestamp():
            return None
        return self.cache[scope]
