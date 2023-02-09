import argparse
import argparse as A
import asyncio as aio
from typing import Union

from doter.commands import BaseCommand
from doter.commands.install import InstallCommand, InstallArgs


def parse_args() -> BaseCommand:
    COMMANDS = [
        InstallCommand,
    ]
    arg_parser = argparse.ArgumentParser()
    subparsers = arg_parser.add_subparsers(dest="action")
    trigger_map = {}

    for command in COMMANDS:
        trigger_map[command.trigger] = command
        sub_parser = subparsers.add_parser(command.trigger)
        command.create_parser_args(sub_parser)

    args_raw = arg_parser.parse_args()
    cmd = trigger_map[args_raw.action]
    args = cmd.arg_class(**args_raw.__dict__)
    return cmd(args)

async def main(args):
    pass


if __name__ == "__main__":
    cmd = parse_args()
    print(cmd.args)
    aio.run(main(None))
