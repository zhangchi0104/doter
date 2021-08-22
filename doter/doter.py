from copy import copy
from datetime import time
from doter.reporter import CliReporter
from doter.lib import dispatch_item
from typing import List
from doter.typings import DotFileConfig
from doter.events import EventPublisher
from envyaml import EnvYAML
from os.path import exists, expanduser, abspath, islink
from os import symlink
from subprocess import run as run_cmd
from pathlib import Path
import time


class DoterApp(EventPublisher):
    def __init__(self, config='./config.yml'):
        super().__init__()
        yaml = EnvYAML(config)
        self._dotfiles = yaml['files']
        self.add_subscriber(CliReporter())

    def _dispatch_item(self, config_item: DotFileConfig):
        """[summary]

        Args:
            config_item (DotFileConfig): [description]
        """
        pre_exec_hooks = config_item.get('before_setup', [])
        src_raw = config_item.get('src', False)
        dst_raw = config_item.get('dst', False)

        if bool(src_raw) ^ bool(dst_raw):
            raise KeyError(
                'src or dst is missing. You must provide all of them or none of them'
            )

        src = expanduser(config_item['src'])
        dst = abspath(config_item['dst'])
        if (exists(src) or
                islink(src)) and not config_item.get('force_override', False):
            self.publish(
                'log_message',
                f'⚠️ skipping {config_item["dst"]} -> {config_item["src"]}, ' +
                'because the source link/file already exist')
            return

        self._exec_hooks(pre_exec_hooks, 'pre')

        self.make_symlink(src, dst)
        self.publish('update_progress', {
            'message':
            f'🔗 Linked {config_item["dst"]} -> {config_item["src"]}'
        })
        post_exec_hooks = config_item.get('after_setup', [])
        self._exec_hooks(post_exec_hooks, 'post')

        self.publish(
            'log_message',
            f'✅ Successfully installed {config_item["dst"]} -> {config_item["src"]}'
        )

    def _exec_hooks(self, hooks: List[str], which: str):
        if len(hooks) < 1:
            return
        for cmd in hooks:
            self.publish(
                'update_progress',
                {'message': f'🚧 Executing {which}-install hook: ' + cmd})
            self._execute_shell(cmd.split(' '))

    def install(self, dry_run=False, *targets):
        """Install all the dotfiles in the specified by targets,
        default to all specified in the config.yml

        Args:
            dry_run (bool, optional): [description]. Defaults to False.
        """

        print(dry_run, targets)
        if len(targets) > 0:
            plans = [self._dotfiles[v] for v in targets]
        else:
            plans = self._dotfiles.values()

        if dry_run:
            self._print_plans(plans)
            return

        self.publish('install_start', len(plans))
        for plan in plans:
            self._dispatch_item(plan)
            self.publish(
                'update_progress', {
                    'message':
                    f'✅ Done processing {plan["dst"]} -> {plan["src"]}',
                    'advance': 1
                })
            time.sleep(1)
        self.publish('install_complete')

    def backup(self):
        """
        copy all the existing files to the project folder
        """
        for config in self._dotfiles.values():
            if not islink(config['src']):
                copy(expanduser(config['src']), expanduser(config['dst']))
                print(f'copied {config["src"]} to {config["dst"]}')
            elif islink(config['src']):
                print(
                    f'Skipping backing up {config["src"]}, because it is a symlink'
                )

    def _execute_shell(self, args: list):
        proc = run_cmd(args)
        if proc.returncode != 0:
            raise RuntimeError(
                f'Error occured when running command"{" ".join(args)}"' +
                f'with return code {proc.returncode}')

    def make_symlink(self, src: str, dst: str):
        # mimics the behaviour of mkdir -p
        p = Path(dst)
        p.parent.mkdir(parents=True, exist_ok=True)
        symlink(dst, src)

    def _print_plans(self, plans: list):
        for i, plan in enumerate(plans):
            print(f'Item {i+1}')
            print('=' * 40)
            print(f"Linking file: {plan['dst']} -> {plan['src']}")
            print(f"Force Override: {plan.get('force_override', False)}")
            print("Pre Install Hook:")
            for hook in plan.get('before_setup'):
                print(f'\t- {hook}')

            print("Post Install Hook:")
            for hook in plan.get('after_setup'):
                print(f'\t- {hook}')