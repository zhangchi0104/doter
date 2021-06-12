#!/usr/bin/env python
# -*- coding: utf-8 -*-
from doter.typings import ConfigFile, DotFileConfig, Dict, List
from yaml import load as load_yaml, FullLoader
from copy import deepcopy
from os.path import exists, expanduser, islink, abspath
from subprocess import run as run_cmd
from os import symlink, stat

def load_config(path: str):
    f = open(path, 'r')
    config = load_yaml(f, Loader=FullLoader)
    f.close()

    return ConfigFile(config)


def execute_shell(args: list):
    proc = run_cmd(args)
    if proc.returncode != 0:
        raise RuntimeError(
            f'Error occured when running command"{" ".join(args)}"' +
            'with return code {proc.returncode}')


def dispatch_item(config_item: DotFileConfig):
    pre_exec_hooks = config_item.get('before_setup', None)
    src = expanduser(config_item['src'])
    print(src, config_item['src'])
    if pre_exec_hooks and len(pre_exec_hooks) > 0:
        for cmd in pre_exec_hooks:
            execute_shell(cmd.split(' '))
    if config_item.get('force_override', False) or (not exists(src)
                                                    and not islink(src)):
        from_file = abspath(config_item['dst'])
        symlink(from_file, src)
    else:
        print(f'skipping {config_item["dst"]} -> {config_item["src"]}' +
              ', because the file/link already exists')
    post_exec_hooks = config_item.get('after_setup', None)
    if post_exec_hooks and len(post_exec_hooks) > 0:
        for cmd in post_exec_hooks:
            execute_shell(cmd.split(' '))


def resolve_files(config: ConfigFile):
    dotfiles = deepcopy(config['files'])
    for key, _ in dotfiles.items():
        dotfiles[key]['src'] = key
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


