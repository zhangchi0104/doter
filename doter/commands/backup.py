from typing import List, Tuple, Union

from doter import events
from .command import Command
from pathlib import Path
from shutil import move
from ..utils import create_traceback, link

import yaml

__CLASS_NAME__ = "Backup"
__COMMAND_NAME__ = "backup"

Args = Union[List[str], Tuple[str]]


class Backup(Command):
    def __init__(self, dotfiles, dotfiles_dir, event_bus):
        super().__init__(dotfiles, dotfiles_dir, event_bus)

    async def __call__(self, *args):
        if len(args) < 2:
            await self._event_bus.publish(
                events.ERROR, message='Usage: <name> <dotfile>:<target>')
            return
        name, specs = self.parse_args(args)
        try:
            for src, dst in specs:
                src_path = Path(src).expanduser().absolute()
                dst_path = Path(dst).expanduser().absolute()
                if not src_path.exists():
                    raise FileNotFoundError(src)

                move(src_path, dst_path)
                link(self._dotfiles_dir, str(src_path), str(dst_path), True)

            with open(self._config_path, 'w') as f:
                conf = self._config._raw
                files = dict(specs)
                if name not in conf['config'].keys():
                    conf['config'][name] = {'files': files}
                else:
                    conf['config'][name]['files'] = files
                yaml.dump(conf, f)
            await self._event_bus.publish('backup/done')
        except FileNotFoundError as err:
            tb = create_traceback(FileNotFoundError, err, err.__traceback__)
            await self._event_bus.publish(events.ERROR,
                                          message="dotfile not found",
                                          traceback=tb)

    def parse_args(self, args: Args) -> Tuple[str, List[Tuple[str, str]]]:
        task = args[0]
        res = []
        for arg in args[1::]:
            items = arg.split(':')
            if len(items) != 2:
                raise ValueError(f'Invalid spec for backup ({arg})')
            res.append((items[0], items[1]))

        return task, res
