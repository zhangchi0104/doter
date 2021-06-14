from click import group, option, pass_context
from shutil import copy
from os.path import islink, expanduser
from click.decorators import argument

from rich import text
from doter.lib import load_config, resolve_files, resolve_deps, dispatch_item
from rich.progress import track, Progress, SpinnerColumn, TextColumn
from time import sleep, time


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
@argument('targets', nargs=-1)
@pass_context
@option('--dry-run', '-d', is_flag=True, help='specify config file')
def link(ctx, dry_run: bool, targets):
    console = ctx.obj['console']
    config = ctx.obj['config']
    configs = load_config(config)
    dotfiles = resolve_files(configs)
    if len(targets):
        plans = [dotfiles[v] for v in targets] 
    else:
        plans = dotfiles.values()
    if dry_run:
        for i, plan in enumerate(plans):
            print(f'{i+1}. {plan}')
        return
    else:
        with Progress(SpinnerColumn(),
                      TextColumn('({task.completed}/{task.total})'),
                      TextColumn('[progress.description]{task.description}'),
                      console=console,
                      transient=True) as progress:
            task = progress.add_task('linking items', total=len(plans))
            start_time = time()
            
            for plan in plans:
                dispatch_item(plan, console, progress, task)
                progress.update(
                    task,
                    description=
                    f'✅ Done processing {plan["dst"]} -> {plan["src"]}',
                    advance=1)
                sleep(1)
            end_time = time()
        console.log(f'✨ Completed in {(end_time - start_time):.2f}s')


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
        elif islink(config['src']):
            print(
                f'Skipping backing up {config["src"]}, because it is a symlink'
            )
        else:
            print(f"Backup: {config['src']} -> {config['dst']}")
