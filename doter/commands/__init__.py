from argparse import ArgumentParser
from typing import List, Generic, Type, TypeVar, get_args, Dict, Any

A = TypeVar('A')
from pydantic import BaseModel
from pydantic.fields import SHAPE_LIST, SHAPE_TUPLE, SHAPE_ITERABLE, SHAPE_SET, SHAPE_DEQUE, SHAPE_SEQUENCE

from doter.parser import ConfigFile, ConfigItem
from typing import List
from joblib import Parallel, delayed
from asyncio import Queue

ITERABLE_SHAPES = [
    SHAPE_LIST, SHAPE_TUPLE, SHAPE_ITERABLE, SHAPE_SET, SHAPE_DEQUE,
    SHAPE_SEQUENCE
]


class ArgsBase(BaseModel):
    items: List[str] = []
    config: str = "test/test.yml"


class BaseCommand(Generic[A]):
    trigger = ""
    UIClass = object

    @classmethod
    def from_args_dict(cls, args_dict: Dict[str, Any], q: Queue):
        args = cls.arg_class(**args_dict)
        return cls(args, q)

    def __init__(self, args: A, q: Queue):
        self.args = args

    def run(self, config: ConfigItem):
        pass

    def __call__(self, config: ConfigFile):
        print(config)
        items = self.args.items if len(
            self.args.items) != 0 else config.items.keys()
        Parallel()(delayed(self._prepare_run)(item, config) for item in items)

    def _prepare_run(self, key: str, config: ConfigFile):
        try:
            item = config.items[key]
            self.run(item)
        except KeyError as e:
            print(e)

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
    def arg_class(cls) -> Type[A]:
        return get_args(cls.__orig_bases__[0])[0]