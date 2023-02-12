from . import ArgsBase, BaseCommand
from ..parser import ConfigItem
from pydantic import BaseModel
from typing import List


class InstallArgs(ArgsBase):
    items: List[str] = []
    links_only: bool = False
    dry_run: bool = False
    force: bool = False


class InstallCommand(BaseCommand[InstallArgs]):
    arg_class = InstallArgs
    trigger = "install"

    def run(self, item: ConfigItem):
        self.args
