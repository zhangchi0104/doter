from typing import List, Callable, Dict

from dataclasses import dataclass
import asyncio


@dataclass
class EventBus(object):
    """
    EventBus is used to publish and dispatch events in
    an async manner. Currently used for UI
    """
    _subscribers: Dict[str, List[Callable]]

    def __init__(self):
        self._subscribers = dict()

    def subscribe(self, topic: str, callback: Callable):
        """
        Subscribe to an event with a callback function function

        Args:
            callback (Callable): The function to be called when
            the event is published. It should take keyword arguments (**kwargs)
        """
        if topic not in self._subscribers.keys():
            self._subscribers[topic] = [callback]
            return
        self._subscribers[topic].append(callback)

    async def publish(self, topic: str, **kwargs):
        """
        publish an event asyncrously

        Args:
            topic (str): the identifier of the event
            **kwrags: the extra context to be passed to the subscribers
        """
        subscribers = self._subscribers.get(topic, None)
        if subscribers != None:
            return await asyncio.gather(
                *[asyncio.create_task(s(**kwargs)) for s in subscribers], )
        return None
