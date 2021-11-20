import pytest 
import doter.eventbus as eventbus
import asyncio
@pytest.fixture
def event_bus():
    return eventbus.EventBus()


def test_subsribe(event_bus):
    event_bus.subscribe('test', print)
    assert len(event_bus._subscribers['test']) == 1

@pytest.mark.asyncio
async def test_publish(event_bus):
    l = []

    async def cb(ev):
        print('called') 
        l.append(ev)
    event = eventbus.Event[int](1)
    event_bus.subscribe('test', cb)
    await event_bus.publish('test', event)
    assert len(l) == 1
    assert l[0] is event
