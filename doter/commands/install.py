from . import ArgsBase, BaseCommand

from ..config import ConfigItem
from typing import List, Union
from doter.ui.install_ui import InstallUI, InstallUIEvent, InstallAction
from ..utils import sh
from os import symlink

from ..utils import LoggerMixin
from shutil import rmtree
from pydantic import Field


class InstallArgs(ArgsBase):
    links_only: bool = Field(False,
                             description="only create symlinks without hooks",
                             alias="l")
    dry_run: bool = Field(False, description="Show execution plan", alias="d")
    force: bool = Field(False, description="Override existing files/links")


class InstallCommand(BaseCommand[InstallArgs, InstallUIEvent], LoggerMixin):
    trigger = "install"
    UIClass = InstallUI

    def create_link(self, key: str, managed_path: str, link_path: str):
        managed_p = self.resolve_path(managed_path)
        link_p = self.resolve_path(link_path)

        if link_p.exists() and not self.args.force:
            raise FileExistsError(
                f"target path '{link_path}' already exists and --force is not specified "
            )

        self._dispatch_ui_action(
            InstallAction.STEP, {
                "name": key,
                "msg": f"Linking {managed_path} -> {link_path}"
            })

        rmtree(link_p, ignore_errors=True)
        link_p.parent.mkdir(parents=True, exist_ok=True)
        symlink(managed_p, link_p)

    async def run(self, key: str, item: ConfigItem):

        try:
            total_steps = self.calculate_steps(item)
            self._dispatch_ui_action(InstallAction.INIT, {
                "name": key,
                "total_steps": total_steps
            })
            # Execute Pre-install hooks
            await self.execute_hooks(key, item.before)
            # Create Symbolic links
            for managed_path, original_path in item.mappings.items():
                self.create_link(key, managed_path, original_path)
            # Execute Post-install hooks
            await self.execute_hooks(key, item.after)
            self._dispatch_ui_action(InstallAction.DONE, {"name": key})
        # Stop current task when exceptions are raised
        except Exception as e:
            self.error(e)
            self._dispatch_ui_action(InstallAction.ERROR, {
                "name": key,
                "error": e,
            })
            return

    def calculate_steps(self, item: ConfigItem):
        res = 0 if item.before is None or self.args.links_only else len(
            item.before)
        res += 0 if item.after is None or self.args.links_only else len(
            item.after)
        res += len(item.mappings)
        return res

    async def execute_hooks(self, key: str, hooks: Union[List[str], None]):
        if hooks is None:
            return

        for hook in hooks:
            self._dispatch_ui_action(InstallAction.STEP, {
                "name": key,
                "msg": f"executing: {hook}"
            })
            await sh(hook)

    def _dispatch_ui_action(self, action: InstallAction, payload: dict):
        self.notify_ui(InstallUIEvent(action=action, payload=payload))
