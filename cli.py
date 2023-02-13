import argparse
from asyncio import run, create_task

from typing import Type, Dict

from doter.commands import BaseCommand
from doter.commands.install import InstallCommand
from doter.parser import from_file


def parse_args():
    COMMANDS = [
        InstallCommand,
    ]
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--config",
                            "-c",
                            help="path to config file",
                            default="test/test.yml")
    subparsers = arg_parser.add_subparsers(dest="action")
    trigger_map: Dict[str, Type[BaseCommand]] = {}

    for command in COMMANDS:
        trigger_map[command.trigger] = command
        sub_parser = subparsers.add_parser(command.trigger)
        command.create_parser_args(sub_parser)

    args_raw = arg_parser.parse_args()
    cls: BaseCommand = trigger_map[args_raw.action]
    cmd = cls.from_args_dict(args_raw.__dict__)

    return cmd


async def main(cmd: BaseCommand):
    config_file = from_file(cmd.args.config)
    q = cmd.queue
    ui = cmd.UIClass(q)
    create_task(ui())
    await (cmd(config_file))


if __name__ == "__main__":
    cmd = parse_args()
    run(main(cmd))