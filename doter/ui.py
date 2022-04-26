from rich.progress import Progress, TextColumn, SpinnerColumn
from .eventbus import EventBus


class RichUI(object):
    """ RichUI

    A fancy command line progress display, it listens to
    events from the event bus

    """
    STATUS_EMOJIS = {
        "completed": ":white_check_mark:",
        "error": ":cross_mark:",
        "running": ":construction:"
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
        event_bus.subscribe('install/init', self._on_init)
        event_bus.subscribe('install/update', self._on_update)
        event_bus.subscribe('install/done', self._on_completed)
        event_bus.subscribe('install/error', self._on_error)

    async def _on_error(self, **kwargs):
        """
        Callback function when an error occured
        """
        # extract information from context
        name = kwargs['name']
        task_id = self._task_dict[name]
        tb = kwargs['traceback']

        # Update progress to display error
        # and display traceback
        self._progress.update(
            task_id,
            description="Failed",
            status=self.STATUS_EMOJIS['error'],
        )
        self._progress.console.print(tb)

    async def _on_completed(self, **params):
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

    async def _on_init(self, **params):
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

    async def _on_update(self, **params):
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

    @property
    def progress(self):
        return self._progress
