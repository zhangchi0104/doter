#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rich.progress import Progress, TaskID
from doter.typings import ConfigFile, DotFileConfig, Dict, List
from yaml import load as load_yaml, FullLoader
from copy import deepcopy
from os.path import exists, expanduser, islink, abspath
from subprocess import run as run_cmd
from os import symlink, stat
from rich.console import Console


def load_config(path: str):
    f = open(path, 'r')
    config = load_yaml(f, Loader=FullLoader)
    f.close()

    return config


def _should_create_link(path: str):
    """
    cerate link only if there is no file or no link
    """
    return (not exists(path)) and (not exists(path))


def execute_shell(args: list):
    proc = run_cmd(args, shell=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f'Error occured when running command"{" ".join(args)}"' +
            'with return code {proc.returncode}')


def dispatch_item(config_item: DotFileConfig, console: Console,
                  progress: Progress, task_id: TaskID):
    pre_exec_hooks = config_item.get('before_setup', None)
    src = expanduser(config_item['src'])
    if (exists(src) or islink(src)):
        console.log(
            f'⚠️  Skipping {config_item["dst"]} -> {config_item["src"]}' +
            ', because the file/link already exists')
        return

    if pre_exec_hooks and len(pre_exec_hooks) > 0:
        for cmd in pre_exec_hooks:
            progress.update(task_id,
                            description='🚧 Executing Pre-install hook: ' + cmd)
            execute_shell(cmd.split(' '))
    if config_item.get('force_override', False) and _should_create_link(
            config_item['src']):
        from_file = abspath(config_item['dst'])
        symlink(from_file, src)
        progress.update(
            f'🚧 Linking {config_item["dst"]} -> {config_item["src"]}')

    post_exec_hooks = config_item.get('after_setup', None)
    if post_exec_hooks and len(post_exec_hooks) > 0:
        for cmd in post_exec_hooks:
            progress.update('Executing post-install hook: ' + cmd)
            execute_shell(cmd.split(' '))

    console.log(
        f'✅ Successfully linked {config_item["dst"]} -> {config_item["src"]}')


def resolve_files(config: ConfigFile):
    dotfiles = deepcopy(config['files'])
    return dotfiles


def resolve_deps(dotfiles: Dict[str, DotFileConfig]):
    def _do_resolve_deps(_curr: str, _dotfiles: Dict[str, DotFileConfig],
                         _deps: List[DotFileConfig], _visited: List[str]):
        if _curr in _visited:
            return
        _visited.append(_curr)
        curr_config = _dotfiles[_curr]
        curr_dep = curr_config.get('deps', None)
        # if
        if curr_dep is None:
            _deps.insert(0, curr_config)
        else:
            for dep in curr_dep:
                _do_resolve_deps(dep, _dotfiles, _deps, _visited)
            _deps.append(_dotfiles[_curr])

    visited = []
    deps = []
    for key in dotfiles.keys():
        _do_resolve_deps(key, dotfiles, deps, visited)
    return deps
