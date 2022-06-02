from .command import Command
from ..dotfile import ConfigItem
from pathlib import Path
from ..utils import link, create_traceback
import doter.events as events
import asyncio

__CLASS_NAME__ = "Link"
__COMMAND_NAME__ = "link"


class Link(Command):
    def __init__(self, config, dotfiles_dir, event_bus):
        super().__init__(config, dotfiles_dir, event_bus)

    async def __call__(self, *args, force=False):
        try:
            config_items = args if len(args) > 0 else self._config.all_items
            print(self._config)
            await asyncio.gather(*[
                self._do_link(self._config.items[key], force)
                for key in config_items
            ])
        except KeyError as e:
            traceback = create_traceback(KeyError, e, e.__traceback__)
            await self._event_bus.publish(
                events.TASK_ERROR,
                name=None,
                description=f'Key does not exist: {str(e)}',
                traceback=traceback,
            )

    async def _do_link(self, config: ConfigItem, force: bool):
        try:
            for src, dst in config.files.items():
                abs_src = Path(src)
                if (not force) and abs_src.exists():
                    raise RuntimeError(
                        f'{src} already exists, and "--force is not set"')
                link(self._dotfiles_dir, src, dst, force)
        except RuntimeError as e:
            await self._publish(
                events.ERROR,
                descrption=str(e),
                traceback=e,
            )
