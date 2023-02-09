from argparse import ArgumentParser

from pydantic import BaseModel
from pydantic.utils import  lenient_issubclass
from doter.parser import ConfigFile


class BaseCommand(object):
    arg_class = BaseModel
    trigger = ""

    def __init__(self, args: arg_class):
        self.args = args

    async def run(self, config: ConfigFile):
        pass

    @classmethod
    def create_parser_args(cls, parser: ArgumentParser):
        for key, field in cls.arg_class.__fields__.items():
            params = {
                "default": field.default,

                "help": field.field_info.description or "",
            }
            if isinstance(field.default, bool) and not field.default:
                params['action'] = "store_true"
            elif isinstance(field.default, bool) and field.default:
                params['action'] = "store_false"
            field_name = key if key == "items" else f"--{key}"

            if not field_name.startswith("--"):
                params["nargs"] = "?"
            parser.add_argument(field_name, **params)




