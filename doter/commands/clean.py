from .command import Command
import asyncio
from ..utils import create_traceback
from ..dotfile import ConfigItem
from pathlib import Path
import doter.events as events

__CLASS_NAME__ = "Clean"
__COMMAND_NAME__ = "clean"


class Clean(Command):
    def __init__(self, dotfiles, dotfiles_dir, event_bus):
        super().__init__(dotfiles, dotfiles_dir, event_bus)

    async def __call__(self, *args):
        try:
            config_items = args if len(args) > 0 else self._config.all_items
            print(self._config)
            await asyncio.gather(*[
                self._do_clean(self._config.items[key]) for key in config_items
            ])
        except KeyError as e:
            traceback = create_traceback(KeyError, e, e.__traceback__)
            await self._event_bus.publish(
                events.TASK_ERROR,
                name=None,
                description=f'Key does not exist: {str(e)}',
                traceback=traceback,
            )

    async def _do_clean(self, item: ConfigItem):
        try:
            for src in item.files.keys():
                src_path = Path(src).expanduser().absolute()
                if src_path.is_symlink():
                    src_path.unlink()
                    await self._publish(events.DONE, message=f'removed {src}')
                else:
                    raise RuntimeWarning(
                        f'Skipping {src}: not a symbolic link')
        except RuntimeWarning as warning:
            await self._publish(events.WARN, message=str(warning))
