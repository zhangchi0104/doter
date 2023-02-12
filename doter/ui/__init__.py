from typing import Generic, TypeVar, Type
from asyncio import Queue
from pydantic import BaseModel


class UIEventBase(BaseModel):
    name: str


T = TypeVar('T', bound=UIEventBase)


class UIBase(Generic[T]):
    def __init__(self, q: Queue):
        self._q = q

    async def __call__(self):
        while True:
            item: T = await self._q.get()
            handler = getattr(self, f"on_{item.name}")
            handler(item)
            self._q.task_done()
