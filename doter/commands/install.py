from .command import Command
from ..utils import create_traceback
import asyncio
from ..utils import link, run_hooks
from pathlib import Path
from ..tpyings import ConfigItem

__CLASS_NAME__ = "Install"
__COMMAND_NAME__ = "install"


class Install(Command):
    def __init__(self, dotfiles, dotfiles_dir, event_bus):
        super().__init__(dotfiles, dotfiles_dir, event_bus)

    async def __call__(self, *args, force=False):
        try:
            config_items = args if len(args) > 0 else self._dotfiles.keys()
            await asyncio.gather(*[
                self._do_isntall(item, self._dotfiles[item], force)
                for item in config_items
            ])
        except KeyboardInterrupt:
            await self._event_bus.publish('install/sigint')

    async def _do_isntall(self, key: str, config: ConfigItem, force: bool):
        src = config.get('src', None)
        dst = config.get('dst', None)
        if src is None or dst is None:
            return
        if not force and Path(src).expanduser().absolute().exists():
            return
        pre_install_hooks = config.get('before_setup', [])
        post_install_hooks = config.get('after_setup', [])
        total_steps = len(pre_install_hooks) + len(post_install_hooks) + 1
        await self._event_bus.publish(
            'install/init',
            name=key,
            description='Preparing for setup',
            total=total_steps,
        )
        try:
            # Run pre-install hoooks
            await run_hooks(pre_install_hooks, self._event_bus, key)
        except RuntimeError as e:
            traceback = create_traceback(RuntimeError, e, e.__traceback__)
            await self._event_bus.publish(
                'install/error',
                name=key,
                description=f'Pre-Install hook: {str(e)}',
                traceback=traceback,
            )
            return

        # make symlink
        link(self._dotfiles_dir, src, dst, force)
        try:
            # run post-install hooks
            await run_hooks(post_install_hooks, self._event_bus, key)
        except RuntimeError as e:
            traceback = create_traceback(RuntimeError, e, e.__traceback__)
            await self._event_bus.publish(
                'install/error',
                name=key,
                traceback=traceback,
            )
            return
        await self._event_bus.publish('install/done', name=key)
