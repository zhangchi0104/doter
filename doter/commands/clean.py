from .command import Command
import asyncio
from ..utils import run_hooks
from pathlib import Path
from os import remove

__CLASS_NAME__ = "Clean"
__COMMAND_NAME__ = "clean"


class Clean(Command):
    def __init__(self, dotfiles, dotfiles_dir, event_bus):
        super().__init__(dotfiles, dotfiles_dir, event_bus)

    async def __call__(self, *args):
        if len(args) == 0:
            await asyncio.gather(*[
                self._do_clean(item_key) for item_key in self._dotfiles.keys()
            ])
        else:
            await asyncio.gather(
                *[self._do_clean(item_key) for item_key in args])

    def _remove_link(self, link_path: str):
        p = Path(link_path).expanduser().absolute()
        if not p.is_symlink():
            print(f"Skipping {link_path}, it is not a symbolic link")
            return
        p.unlink()
        # remove(p)

    async def _do_clean(self, item_key: str):
        item = self._dotfiles[item_key]
        hooks_task = None
        hooks = item.get('cleanup', None)
        if hooks is not None:
            hooks_task = run_hooks(hooks)
        self._remove_link(item["src"])
        if hooks_task:
            await hooks_task
