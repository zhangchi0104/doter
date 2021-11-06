from typing import List
import envyaml
from .tpying import ConfigItem
from typing import List
from pathlib import Path
import asyncio, os


class DoterApp(object):
    def __init__(self, config='./config.yaml', dotfiles_dir='./dotfiles'):
        self._config = envyaml.EnvYAML(config)
        self._dotfiles_dir = Path(dotfiles_dir)

    async def _do_isntall(self, key: str, config: ConfigItem, force: bool):
        src = config.get('src', None)
        dst = config.get('dst', None)
        if src is None or dst is None:
            return
        if not force and Path(src).expanduser().absolute().exists():
            print(f'Skipping {key}: file already exists')
            return
        # Run pre-install hoooks
        await self._run_hooks(config.get('before_setup', []))
        # make symlink
        self._link(src, dst, force)
        # run post-install hooks
        await self._run_hooks(config.get('after_setup', []))
        print('Done')

    async def install(self, *args, force=False):
        print(force, args)
        config_items = args if len(args) > 0 else self._config['files'].keys()
        try:
            await asyncio.gather(*[
                self._do_isntall(item, self.dotfiles[item], force)
                for item in config_items
            ])
        except RuntimeError as e:
            print(e)
            exit(1)

    async def _run_hooks(self, hooks: List[str]):
        home_dir = os.getenv('HOME')
        if home_dir is None:
            raise RuntimeError('environment variable $HOME is not set')
        print(hooks)
        for cmd in hooks:
            proc = await asyncio.create_subprocess_shell(
                cmd.replace('~', home_dir),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
                shell=True)
            _, stderr = await proc.communicate()
            retcode = proc.returncode
            if retcode != 0:
                raise RuntimeError(
                    f'Hook {cmd} exited with code {retcode}: {stderr.decode()}'
                )

    def _link(self, src: str, dst: str, force: bool):

        abs_src = os.path.abspath(os.path.expanduser(src))
        abs_dst = os.path.join(self._dotfiles_dir, os.path.expanduser(dst))
        abs_dst = os.path.abspath(abs_dst)
        abs_src = Path(abs_src)
        print(abs_src.is_symlink())
        print(abs_src.is_file())
        print("locals")
        print(locals())
        if force and abs_src.is_symlink():
            abs_src.unlink()
            print(f"Unlinking {abs_src}")
        elif force and abs_src.is_file():
            os.remove(abs_src)
            print(f"Removing {abs_src}")
        elif force and abs_src.is_dir():
            os.removedirs(abs_src)
        abs_src.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(src=abs_dst, dst=abs_src)
    
    async def link(self, *args, force=False):
        print(force, args)
        config_items = args if len(args) > 0 else self._config['files'].keys()
        try:
            await asyncio.gather(*[
                self._do_link(item, self.dotfiles[item], force)
                for item in config_items
            ])
        except RuntimeError as e:
            print(e)
            exit(1)
    
    async def _do_link(self, key: str, config: ConfigItem, force: bool):
        src = config.get('src', None)
        dst = config.get('dst', None)
        if src is None or dst is None:
            return
        if not force and Path(src).expanduser().absolute().exists():
            print(f'Skipping {key}: file already exists')
            return
        
        self._link(src,dst, force)
            
     
        
    @property
    def dotfiles(self):
        return self._config['files']
