#!/usr/bin/env python
# -*- coding: utf-8 -*-
from click.decorators import group
from typings import ConfigFile, DotFileConfig, Dict, List
from yaml import load as load_yaml, FullLoader
from copy import deepcopy
from os import symlink, stat
from shutil import copy
from os.path import exists, expanduser, islink, abspath
from subprocess import run as run_cmd
from click import group, option, pass_context


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
    for key, file in dotfiles.items():
        if 'before_setup' in file.keys() and file['before_setup'] is not None:
            dotfiles[key]['before_setup'] = [
                command.split(' ') for command in file['before_setup']
            ]
        if 'after_setup' in file.keys() and file['after_setup'] is not None:
            dotfiles[key]['after_setup'] = [
                command.split(' ') for command in file['after_setup']
            ]
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


@group()
@option('--config',
        '-c',
        default='./config.yml',
        show_default=True,
        type=str,
        help='specify config file')
@pass_context
def cli(ctx, config):
    ctx.ensure_object(dict)
    ctx.obj['config'] = config


@cli.command()
@pass_context
@option('--dry-run', '-d', is_flag=True, help='specify config file')
def link(ctx, dry_run: bool):
    config = ctx.obj['config']
    configs = load_config(config)
    dotfiles = resolve_files(configs)
    plans = resolve_deps(dotfiles)
    if dry_run:
        for i, plan in enumerate(plans):
            print(f'{i+1}. {plan}')
        return
    else:
        for plan in plans:
            dispatch_item(plan)


@cli.command()
@pass_context
@option('--dry-run', '-d', is_flag=True, help='specify config file')
def backup(ctx, dry_run):
    config_file = ctx.obj['config']
    configs = load_config(config_file)
    dotfiles = resolve_files(configs)
    for config in dotfiles.values():
        if not dry_run and not islink(config['src']):
            copy(expanduser(config['src']), expanduser(config['dst']))
        elif islink(config):
            print(
                f'Skipping backing up {config["src"]}, because it is a symlink'
            )
        else:
            print(f"Backup: {config['src']} -> {config['dst']}")


if __name__ == '__main__':
    cli(obj={})