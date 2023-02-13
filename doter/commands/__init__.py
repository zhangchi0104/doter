from argparse import ArgumentParser
from enum import Enum
from typing import List, Generic, Type, TypeVar, Union, get_args, Dict, Any

from doter.ui import UIBase, UIEvent
from pydantic import BaseModel
from pydantic.fields import SHAPE_LIST, SHAPE_TUPLE, SHAPE_ITERABLE, SHAPE_SET, SHAPE_DEQUE, SHAPE_SEQUENCE

from doter.parser import ConfigFile, ConfigItem
from typing import List
from asyncio import Queue, gather

ITERABLE_SHAPES = [
    SHAPE_LIST, SHAPE_TUPLE, SHAPE_ITERABLE, SHAPE_SET, SHAPE_DEQUE,
    SHAPE_SEQUENCE
]
Args = TypeVar('Args')

E = TypeVar('E', bound=UIEvent)


class ArgsBase(BaseModel):
    items: List[str] = []
    config: str = "test/test.yml"


class BaseCommand(Generic[Args, E]):
    trigger = ""
    UIClass = UIBase

    @classmethod
    def from_args_dict(cls, args_dict: Dict[str, Any]):
        args = cls.arg_class(**args_dict)
        return cls(args)

    def __init__(self, args: Args):
        self.args = args
        self._queue = Queue()

    async def run(self, key: str, config: ConfigItem):
        pass

    async def __call__(self, config: ConfigFile):
        keys = self.args.items if len(
            self.args.items) != 0 else config.items.keys()
        await gather(*[self._prepare_run(key, config) for key in keys])

    async def _prepare_run(self, key: str, config: ConfigFile):
        try:
            item = config.items[key]
            await self.run(key, item)
        except KeyError as e:
            print(f"{key} does not exist")

    @classmethod
    def create_parser_args(cls, parser: ArgumentParser):
        arg_class = cls.arg_class
        for key, field in arg_class.__fields__.items():
            params = {
                "default": field.default,
                "help": field.field_info.description or "",
            }

            if isinstance(field.default, bool) and not field.default:
                params['action'] = "store_true"
            elif isinstance(field.default, bool) and field.default:
                params['action'] = "store_false"
            field_name = key if field.shape in ITERABLE_SHAPES else f"--{key}"

            if not field_name.startswith("--"):
                params["nargs"] = "?"
            parser.add_argument(field_name, **params)

    @classmethod
    @property
    def arg_class(cls) -> Type[Args]:
        return get_args(cls.__orig_bases__[0])[0]

    @classmethod
    @property
    def ui_event_class(cls) -> Type[E]:
        return get_args(cls.__orig_bases__[0])[1]

    @property
    def queue(self):
        return self._queue

    def notify_ui(self, event: E):
        self._queue.put_nowait(event)
