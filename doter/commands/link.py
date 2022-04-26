from .command import Command
from ..tpyings import ConfigItem
from pathlib import Path
from ..utils import link
import asyncio

__CLASS_NAME__ = "Link"
__COMMAND_NAME__ = "link"


class Link(Command):
    def __init__(self, config, dotfiles_dir, event_bus):
        super().__init__(config, dotfiles_dir, event_bus)

    async def __call__(self, *args, force=False):
        config_items = args if len(args) > 0 else self._config['files'].keys()
        try:
            await asyncio.gather(*[
                self._do_link(item, self._dotfiles[item], force)
                for item in config_items
            ])
        except RuntimeError as e:
            print(e)
            e3it(1)

    async def _do_link(self, key: str, config: ConfigItem, force: bool):
        src = config.get('src', None)
        dst = config.get('dst', None)
        if src is None or dst is None:
            return
        if not force and Path(src).expanduser().absolute().exists():
            print(f'Skipping {key}: file already exists')
            return

        link(self._dotfiles_dir, src, dst, force)
