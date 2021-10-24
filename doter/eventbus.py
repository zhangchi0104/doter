from typing import List, Callable, Dict, TypeVar, Generic, Any

from dataclasses import dataclass
import asyncio 
P = TypeVar('P')
@dataclass
class Event(Generic[P]):
    payload: P

@dataclass
class EventBus(object):
    _subscribers: Dict[str, List[Callable]]

    def __init__(self):
        self._subscribers = dict()
    def subscribe(self,topic: str, callback: Callable):
        if topic not in self._subscribers.keys():
            self._subscribers[topic] = [callback]
            return
        self._subscribers[topic].append(callback)

    def publish(self, topic: str, event: Event[Any]):
        subscribers = self._subscribers.get(topic, None)
        if subscribers != None:
            return asyncio.gather(
                *[asyncio.create_task(s(event)) for s in subscribers],
            )
        return None

