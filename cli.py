import argparse
import argparse as A
from asyncio import Queue

from typing import Type, Dict

from doter.commands import BaseCommand, ArgsBase
from doter.commands.install import InstallCommand
from doter.parser import from_file
from functools import partial


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
    ctor = trigger_map[args_raw.action]
    cmd_partial = partial(ctor.from_args_dict, args_raw.__dict__)

    return cmd_partial


def main(cmd_partial: partial[BaseCommand]):
    q = Queue()
    cmd = cmd_partial(q)
    config_file = from_file(cmd.args.config)
    cmd(config_file)


if __name__ == "__main__":
    cmd = parse_args()
    main(cmd)