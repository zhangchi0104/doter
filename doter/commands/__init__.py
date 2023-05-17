from argparse import ArgumentParser

from typing import List, Generic, Type, TypeVar, get_args, Dict, Any

from ..ui import UIBase, UIEvent
from pydantic import BaseModel
from pydantic.fields import SHAPE_LIST, SHAPE_TUPLE, SHAPE_ITERABLE, SHAPE_SET, SHAPE_DEQUE, SHAPE_SEQUENCE

from ..config import ConfigFile, ConfigItem
from typing import List
from asyncio import Queue, gather
from logging import getLogger

ITERABLE_SHAPES = [
    SHAPE_LIST, SHAPE_TUPLE, SHAPE_ITERABLE, SHAPE_SET, SHAPE_DEQUE,
    SHAPE_SEQUENCE
]
from pathlib import Path


class ArgsBase(BaseModel):
    items: List[str] = []
    config: str = "~/.dotfiles/config.yml"


Args = TypeVar('Args', bound=ArgsBase)

Event = TypeVar('Event', bound=UIEvent)


class BaseCommand(Generic[Args, Event]):
    trigger = ""
    UIClass = UIBase

    @classmethod
    def from_args_dict(cls, args_dict: Dict[str, Any]):
        args = cls.arg_class(**args_dict)
        return cls(args)

    def __init__(self, args: Args):
        self.args = args
        self._queue = Queue()
        self._logger = getLogger(__name__)

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
            short_alias = None
            if field.alias != field.name and isinstance(field.alias, str):
                if len(field.alias) == 1:
                    short_alias = f"-{field.alias}"
                else:
                    raise ValueError(
                        f"{field.alias} havs length {len(field.alias)}, expected to be 1"
                    )

            if isinstance(field.default, bool) and not field.default:
                params['action'] = "store_true"
            elif isinstance(field.default, bool) and field.default:
                params['action'] = "store_false"
            field_name = key if field.shape in ITERABLE_SHAPES else f"--{key}"

            if not field_name.startswith("--"):
                params["nargs"] = "?"
            if short_alias:
                parser.add_argument(field_name, short_alias, **params)
            else:
                parser.add_argument(field_name, **params)

    def resolve_path(self, p: str):
        path = Path(p).expanduser()
        if not path.is_absolute():
            return self.config_dir / path
        else:
            return path

    @property
    def config_dir(self):
        p = Path(self.args.config)
        return p.parent.absolute()

    @classmethod
    @property
    def arg_class(cls) -> Type[Args]:
        return get_args(cls.__orig_bases__[0])[0]

    @classmethod
    @property
    def ui_event_class(cls) -> Type[Event]:
        return get_args(cls.__orig_bases__[0])[1]

    @property
    def queue(self):
        return self._queue

    def notify_ui(self, event: Event):
        self._queue.put_nowait(event)
