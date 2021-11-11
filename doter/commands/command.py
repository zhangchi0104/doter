from pathlib import Path


class Command:
    def __init__(self, config, dotfiles_dir):
        self._config = config
        self._dotfiles_dir = Path(dotfiles_dir)

    def __call__(self):
        raise NotImplementedError()

    @property
    def _dotfiles(self):
        return self._config['files']
