from pathlib import Path
import signal
import asyncio
import importlib
import os
from rich.traceback import install as install_traceback

from typing import Any
from .eventbus import EventBus
from .ui import RichUI

EXCLUDED_FILES = [
    '.git', '.gitignore', '.gitmodules', '.DS_Store', '__pycache__',
    'command.py'
]


class DoterApp(object):
    """  class for the app
    DoterApp contains for all commands for Fire to look up,
    it will source the commands from the commands modules.
    It will also contain the UI component for the app.

    Note: For Details on the commands see the commands modules
    
    Args:
        config (str): path to the config file
        dotfiles_dir (str): path to the dotfiles directory

    """
    _instance = None

    def __init__(self,
                 config='~/.dotfiles/config.yml',
                 dotfiles_dir='~/.dotfiles'):
        install_traceback(show_locals=True)

        self._config_path = Path(config).expanduser().absolute()
        self._dotfiles_dir = Path(dotfiles_dir).expanduser().absolute()
        self._event_bus = EventBus()
        self._ui_component = RichUI(self._event_bus)
        self._resolve_modules()
        DoterApp._instance = self

    def _resolve_modules(self):
        """
        Resolve the commands modules
        it will import every python source file that is not in the
        "EXCLUDED_FILES". If `__CLASS_NAME__` and `__COMMAND_NAME__`
        it will instantiate the class and bind it to the given
        `__COMMAND_NAME__`

    
        """
        commands_dir = Path(__file__).parent / 'commands'
        for fn in os.listdir(commands_dir):
            if fn.endswith('.py') and not fn.startswith(
                    '_') and fn not in EXCLUDED_FILES:
                module: Any = importlib.import_module(
                    'doter.commands.{}'.format(fn[:-3]))
                class_name = module.__CLASS_NAME__
                cmd_name = module.__COMMAND_NAME__
                cls = getattr(module, class_name)
                cmd = cls(self._config_path, self._dotfiles_dir,
                          self._event_bus)
                wrapped_cmd = self._ui_wrapper(cmd.__call__)
                setattr(self, cmd_name, wrapped_cmd)

    def _ui_wrapper(self, func):
        """
        _ui_wrapper is used to wrap the command function
        so the progress bar can be started and ended properly

        Args:
            func (callable): the command function / method to be wrapped

        Returns:
            callable: the wrapped function
        """
        async def inner(*args, **kwargs):
            self._ui_component.progress.start()
            await func(*args, **kwargs)
            self._ui_component.progress.stop()

        return inner

    @classmethod
    def _get_instance(cls):
        """
        _get_instance is used to get current instance exteranlly,
        primarily used in handle Exceptions
        
        Returns:
            DoterApp 
        """
        if cls._instance is None:
            raise ValueError("No running DoterApp instance")
        return cls._instance

    def _stop(self):
        """
        _stop stops the progress bar without using the eventbus

        NOTE: this method should only be used when handling exceptions
        """
        self._ui_component.progress.stop()


if __name__ == '__main__':
    app = DoterApp()
