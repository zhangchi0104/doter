from doter import events
from doter.dotfile import ConfigItem
from .command import Command
from ..utils import create_traceback
import asyncio
from ..utils import link, run_hooks
from pathlib import Path

__CLASS_NAME__ = "Install"
__COMMAND_NAME__ = "install"


class Install(Command):
    def __init__(self, dotfiles, dotfiles_dir, event_bus):
        super().__init__(dotfiles, dotfiles_dir, event_bus)

    async def __call__(self, *args, force=False):
        try:
            config_items = args if len(args) > 0 else self._config.all_items
            print(self._config)
            await asyncio.gather(*[
                self._do_isntall(key, self._config.items[key], force)
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
            return

    async def _do_isntall(self, key: str, config: ConfigItem, force: bool):
        pre_install_hooks = config.pre_hooks
        post_install_hooks = config.post_hooks
        total_steps = len(pre_install_hooks) + len(post_install_hooks) + len(config.files)
        await self._event_bus.publish(
            events.TASK_INIT,
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
                events.TASK_ERROR,
                name=key,
                description=f'Pre-Install hook: {str(e)}',
                traceback=traceback,
            )
            return

        # make symlink
        try:
            for src, dst in config.files.items():
                abs_src = Path(src)
                if (not force) and abs_src.exists():
                    raise RuntimeError(
                        f'{src} already exists, and "--force is not set"')
                link(self._dotfiles_dir, src, dst, force)
        except RuntimeError as e:
            await self._publish(
                events.TASK_ERROR,
                name=key,
                descrption=str(e),
                traceback=e,
            )

        try:
            # run post-install hooks
            await run_hooks(post_install_hooks, self._event_bus, key)
        except RuntimeError as e:
            traceback = create_traceback(RuntimeError, e, e.__traceback__)
            await self._event_bus.publish(
                events.TASK_ERROR,
                name=key,
                traceback=traceback,
            )
            return
        await self._event_bus.publish(events.TASK_DONE, name=key)

