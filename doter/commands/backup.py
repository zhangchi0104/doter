from .command import Command
from pathlib import Path
from shutil import move
import os

import yaml

__CLASS_NAME__ = "Backup"
__COMMAND_NAME__ = "backup"


class Backup(Command):
    def __init__(self, dotfiles, dotfiles_dir, event_bus):
        super().__init__(dotfiles, dotfiles_dir, event_bus)

    def __call__(self, *args):
        if len(args) == 0:
            print("You must provide a path to existing file")
            exit(1)
        try:
            for arg in args:
                print(arg)
                self._do_link(arg)
        except FileExistsError as fee:
            print(fee)
            exit(1)
        except FileNotFoundError as fne:
            print(fne)
            exit(1)

    def _do_link(self, path: str):
        p = Path(path).expanduser().absolute()
        if not p.exists():
            raise FileNotFoundError(f'{path} does not exist')
        if p.is_symlink():
            raise FileExistsError(f'{path} is a symlink')
        src = path
        if str(p).startswith(os.path.expanduser('~')):
            src = src.replace(os.path.expanduser('~'), '~')

        # move the file to dotfiles_dir
        # replace the original one with symlink
        item_name = self._path2name(p)
        dst = self._dotfiles_dir / item_name
        move(str(p), str(dst))
        self._config['files'][item_name] = {'src': src, 'dst': item_name}
        content = yaml.dump(self._config)
        f = open(self._config_path, 'w')
        f.write(content)
        f.close()

    def _path2name(self, path: Path):
        fn = path.name
        item_name = ""
        if fn[0] == '.':
            item_name = fn[1:]
        else:
            item_name = fn
        item_name = item_name.strip().replace(' ', '_')
        if path.is_dir():
            item_name = item_name + '_dir'

        return item_name
