from rich.progress import Progress, TextColumn, SpinnerColumn
from rich.console import Console
from .eventbus import EventBus

import doter.events as events


class RichUI(object):
    """ RichUI

    A fancy command line progress display, it listens to
    events from the event bus

    """
    STATUS_EMOJIS = {
        "completed": ":white_check_mark:",
        "error": ":cross_mark:",
        "running": ":construction:",
        "warning": ":yellow_circle:"
    }

    def __init__(self, event_bus: EventBus):
        """
        Args:
            event_bus (EventBus): the event bus to be subscribed

        Attributes:
            _progress: (Rich.progress.Progress): the progress display
            _task_dict: the mapping of task name to task_id

        
        """
        self._task_dict = dict()
        self._progress = Progress(
            TextColumn("{task.fields[status]}"),  # symbol Column
            SpinnerColumn(),
            TextColumn("{task.fields[name]}"),  # task name column
            TextColumn("({task.completed}/{task.total})"),
            TextColumn("{task.description}"))
        self._console = Console(record=True)
        event_bus.subscribe(events.TASK_INIT, self._on_install_init)
        event_bus.subscribe(events.TASK_UPDATE, self._on_install_update)
        event_bus.subscribe(events.TASK_DONE, self._on_install_completed)
        event_bus.subscribe(events.TASK_ERROR, self._on_install_error)
        event_bus.subscribe(events.DONE, self._on_complete)
        event_bus.subscribe(events.ERROR, self._on_error)

    async def _on_install_error(self, **kwargs):
        """
        Callback function when an error occured
        """
        # extract information from context
        name = kwargs['name']
        task_id = self._task_dict.get(name, None)
        tb = kwargs['traceback']

        # Update progress to display error
        # and display traceback
        if task_id:
            self._progress.update(
                task_id,
                description="Failed",
                status=self.STATUS_EMOJIS['error'],
            )
        self._progress.console.print(tb)

    async def _on_install_completed(self, **params):
        """
        Callback when a task is completed
        """
        # extract variable from context
        name = params['name']
        description = f'Installation of {name} completed'
        task_id = self._task_dict[name]
        # Update the progress bar to display completion message
        self._progress.update(
            task_id,
            description=description,
            status=self.STATUS_EMOJIS['completed'],
            advance=1,
        )

    async def _on_install_init(self, **params):
        """
        Callback for a task initialised
        """
        # extract info
        name = params['name']
        description = params['description']
        total = params['total']

        # Update the progress bar
        task_id = self._progress.add_task(
            description,
            total=total,
            name=name,
            status=self.STATUS_EMOJIS['running'],
        )
        self._task_dict[name] = task_id

    async def _on_install_update(self, **params):
        name = params['name']
        description = params['description']
        task_id = self._task_dict[name]
        self._progress.update(
            task_id,
            advance=1,
            description=description,
        )

    async def on_sigint(self):
        for name, task_id in self._task_dict.items():
            self._progress.update(
                task_id,
                name=name,
                description="Cancelled",
                status=self.STATUS_EMOJIS['error'],
            )

    async def _on_complete(self, **kwargs):
        self._console.print(self.STATUS_EMOJIS['completed'] + " " +
                            kwargs['message'])

    async def _on_error(self, **kwargs):
        tb = kwargs.get('traceback', None)
        if tb:
            self._console.print(tb)
        self._console.print(
            f"{self.STATUS_EMOJIS['error']} {kwargs['message']}")

    async def _on_warning(self, **kwargs):
        tb = kwargs.get('traceback', None)
        if tb:
            self._console.print(tb)
        self._console.print(
            f"{self.STATUS_EMOJIS['warning']} {kwargs['message']}")

    @property
    def progress(self):
        return self._progress
