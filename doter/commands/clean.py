from .command import Command
import asyncio

__CLASS_NAME__ = "Clean"
__COMMAND_NAME__ = "clean"

class Clean(Command):
    def __init__(self, dotfiles, dotfiles_dir):
        super().__init__(dotfiles, dotfiles_dir)

    async def __call__(self, *args, force=False):
        raise NotImplementedError()
    
