from pathlib import Path
from ..eventbus import EventBus
from ..dotfile import parse_config


class Command:
    def __init__(self, config_path, dotfiles_dir, event_bus: EventBus):
        self._config = parse_config(config_path)
        self._config_path = config_path
        self._event_bus = event_bus
        self._dotfiles_dir = Path(dotfiles_dir)

    def __call__(self):
        raise NotImplementedError()

    @property
    def _dotfiles(self):
        return self._config.items

    async def _publish(self, topic, **kwargs):
        await self._event_bus.publish(topic, **kwargs)
