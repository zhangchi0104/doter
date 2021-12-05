from typing import Any
from pathlib import Path
import importlib
import os

EXCLUDED_FILES = [
    '.git', '.gitignore', '.gitmodules', '.DS_Store', '__pycache__',
    'command.py'
]


class DoterApp(object):
    def __init__(self, config='~/.dotfiles/config.yml', dotfiles_dir='~/.dotfiles'):
        self._config_path = Path(config).expanduser().absolute()
        self._dotfiles_dir = Path(dotfiles_dir).expanduser().absolute()
        self._resolve_modules()

    def _resolve_modules(self):
        commands_dir = Path(__file__).parent / 'commands'
        for fn in os.listdir(commands_dir):
            if fn.endswith('.py') and not fn.startswith(
                    '_') and fn not in EXCLUDED_FILES:
                module: Any = importlib.import_module(
                    'doter.commands.{}'.format(fn[:-3]))
                class_name = module.__CLASS_NAME__
                cmd_name = module.__COMMAND_NAME__
                cls = getattr(module, class_name)
                setattr(self, cmd_name,
                        cls(self._config_path, self._dotfiles_dir))


if __name__ == '__main__':
    app = DoterApp()
