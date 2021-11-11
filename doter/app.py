import envyaml
from typing import Any
from pathlib import Path
import importlib
import os

EXCLUDED_FILES = [
    '.git', '.gitignore', '.gitmodules', '.DS_Store', '__pycache__',
    'command.py'
]


class DoterApp(object):
    def __init__(self, config='./config.yaml', dotfiles_dir='./dotfiles'):
        self._config = envyaml.EnvYAML(config)
        self._dotfiles_dir = Path(dotfiles_dir)
        self._resolve_modules()

    def _resolve_modules(self):
        for fn in os.listdir('doter/commands'):
            if fn.endswith('.py') and not fn.startswith(
                    '_') and fn not in EXCLUDED_FILES:
                module: Any = importlib.import_module(
                    'doter.commands.{}'.format(fn[:-3]))
                class_name = module.__CLASS_NAME__
                cmd_name = module.__COMMAND_NAME__
                cls = getattr(module, class_name)
                setattr(self, cmd_name, cls(self._config, self._dotfiles_dir))


if __name__ == '__main__':
    app = DoterApp()
