from os import path
from doter.events import Subscriber
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


class CliReporter(Subscriber):
    def __init__(self):
        super().__init__()
        self._console = Console()
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn('({task.completed}/{task.total})'),
            TextColumn('[progress.description]{task.description}'),
            console=self._console,
            transient=True)
        self._task = None
        self._running_progress = None

    def _on_log_message(self, message):
        self._console.log(message)

    def _on_update_progress(self, payload):
        kwargs = {
            'description': payload['message'],
            'advance': payload.get('advance', None)
        }

        self._running_progress.update(self._task, **kwargs)

    def _on_install_start(self, n_items):
        self._running_progress = self._progress.__enter__()
        self._task = self._running_progress.add_task('Linking Item(s)',
                                                     total=n_items)

    def _on_install_complete(self, payload):
        self._progress.__exit__(None, None, None)
        self._task = None
        self._running_progress = None