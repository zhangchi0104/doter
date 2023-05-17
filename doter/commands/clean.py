import os
from os import PathLike
from doter.config import ConfigItem

from doter.utils import LoggerMixin
from . import ArgsBase, BaseCommand
from doter.ui.cleanup_ui import CleanupAction, CleanupUI, CleanupUIEvent
from shutil import rmtree


class CleanupArgs(ArgsBase):
    force: bool = False,
    dry_run: bool = False,


class CleanupCommand(BaseCommand[CleanupArgs, CleanupUIEvent], LoggerMixin):
    trigger = "clean"
    UIClass = CleanupUI

    def _remove_link(self, p: str, name: str):
        path = self.resolve_path(p)
        if not path.is_symlink() and not self.args.force:
            raise ItemIsNotSymlinkError(path)

        if path.is_symlink():
            path.unlink()
        elif self.args.force:
            if path.is_dir():
                rmtree(path)
            else:
                os.remove(path)

        self._dispatch_ui_action(CleanupAction.DONE, {"name": name})
        self.info(f"Removed '{p}'")

    def _dispatch_ui_action(self, action: CleanupAction, payload: dict):
        self.notify_ui((CleanupUIEvent(action=action, payload=payload)))

    async def run(self, key: str, config: ConfigItem):
        try:
            for link_path in config.mappings.values():
                self._remove_link(link_path, key)
        except ItemIsNotSymlinkError as e:
            self._dispatch_ui_action(CleanupAction.ERROR, {
                "name": key,
                "error": e
            })


class ItemIsNotSymlinkError(Exception):
    def __init__(self, path: PathLike) -> None:
        self._path = path
        super().__init__()

    def __str__(self):
        return f"Item: '{self._path} is not a symlink and '--force' is not set"
