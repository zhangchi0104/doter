from . import ArgsBase, BaseCommand
from ..exceptions import SubprocessError
from ..parser import ConfigItem
from typing import List
from doter.ui.install_ui import InstallUI, InstallUIEvent, InstallAction, InstallUIPayload
from ..utils import sh


class InstallArgs(ArgsBase):
    items: List[str] = []
    links_only: bool = False
    dry_run: bool = False
    force: bool = False


class InstallCommand(BaseCommand[InstallArgs, InstallUIEvent]):
    arg_class = InstallArgs
    trigger = "install"
    UIClass = InstallUI

    async def run(self, key: str, item: ConfigItem):
        total_steps = self.calculate_steps(item)
        action_params = dict(
            action=InstallAction.INIT,
            payload=dict(name=key, total_steps=total_steps),
        )
        self.notify_ui(InstallUIEvent(**action_params))
        self.execute_hooks(key, item.before)
        for mananged_path, original_path in item.mappings.items():
            pass
        self.execute_hooks(key, item.after)

    def calculate_steps(self, item: ConfigItem):
        res = 0 if item.before is None else len(item.before)
        res += 0 if item.after is None else len(item.after)
        res += len(item.mappings)
        return res

    def execute_hooks(self, key: str, hooks: List[str]):
        if hooks == None:
            return
        for hook in hooks:
            try:
                sh(hook)
            except SubprocessError as e:
                params = dict(
                    action=InstallAction.ERROR,
                    payload=dict(name="foo", error=e),
                )
                self.notify_ui(InstallUIEvent(**params))
