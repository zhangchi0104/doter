from pathlib import Path
from typing import Dict
import yaml
from ..tpyings import ConfigItem
from ..eventbus import EventBus


class Command:
    def __init__(self, config_path, dotfiles_dir, event_bus: EventBus):
        self._config_path = config_path
        f = open(config_path, 'r')
        self._config = yaml.load(f, Loader=yaml.Loader)
        self._event_bus = event_bus
        f.close()
        self._dotfiles_dir = Path(dotfiles_dir)

    def __call__(self):
        raise NotImplementedError()

    @property
    def _dotfiles(self) -> Dict[str, ConfigItem]:
        return self._config['files']
