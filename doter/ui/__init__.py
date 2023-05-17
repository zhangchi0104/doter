from enum import Enum
from typing import Generic, TypeVar, Type
from asyncio import Queue
from pydantic.generics import GenericModel
from pydantic import BaseModel

P = TypeVar('P')
A = TypeVar('A', bound=Enum)


class PayloadBase(BaseModel):
    name: str


class ErrorPayload(PayloadBase):
    error: Exception

    class Config:
        arbitrary_types_allowed = True


class UIEvent(GenericModel, Generic[A, P]):
    action: A
    payload: P


T = TypeVar('T', bound=UIEvent)


class UIBase(Generic[T]):
    def __init__(self, q: Queue):
        self._q = q

    async def __call__(self):
        while True:
            item: T = await self._q.get()
            handler = getattr(self, f"on_{item.action.value}")
            handler(item.payload)
            self._q.task_done()

    def __enter__(self):
        return self

    def __exit__(self):
        return None
