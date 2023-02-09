from argparse import ArgumentParser
from typing import List

from . import BaseCommand
from ..parser import ConfigFile
from pydantic import BaseModel

class InstallArgs(BaseModel):
    items: List[str] = []
    links_only: bool = False
    dry_run: bool = False
    force: bool = True
class InstallCommand(BaseCommand):
    arg_class = InstallArgs
    trigger = "install"
    async def run(self, config: ConfigFile):
        pass



