from .command import Command
import asyncio
from ..utils import link, run_hooks
from pathlib import Path
from ..tpyings import ConfigItem

__CLASS_NAME__ = "Install"
__COMMAND_NAME__ = "install"


class Install(Command):
    def __init__(self, dotfiles, dotfiles_dir):
        super().__init__(dotfiles, dotfiles_dir)

    async def __call__(self, *args, force=False):
        print(force, args)
        config_items = args if len(args) > 0 else self._dotfiles.keys()
        try:
            await asyncio.gather(*[
                self._do_isntall(item, self._dotfiles[item], force)
                for item in config_items
            ])
        except RuntimeError as e:
            print(e)
            exit(1)

    async def _do_isntall(self, key: str, config: ConfigItem, force: bool):
        src = config.get('src', None)
        dst = config.get('dst', None)
        if src is None or dst is None:
            return
        if not force and Path(src).expanduser().absolute().exists():
            print(f'Skipping {key}: file already exists')
            return
        # Run pre-install hoooks
        await run_hooks(config.get('before_setup', []))
        # make symlink
        link(self._dotfiles_dir, src, dst, force)
        # run post-install hooks
        await run_hooks(config.get('after_setup', []))
        print('Done')
