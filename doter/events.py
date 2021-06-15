class Subscriber(object):
    def __init__(self):
        super().__init__()
        self._handlers = {}

    def reigster_handler(self, event, handler):
        """[summary]

        Args:
            event ([type]): [description]
            handler ([type]): [description]
        """
        self._handlers[event] = handler

    def handle(self, event, payload):
        if event in self._handlers.keys:
            self._handlers[event](payload)


class EventPublisher(object):
    def __init__(self):
        super().__init__()
        self._subscribers = []

    def add_subscriber(self, subcriber: Subscriber):
        """
        Add a subscriber to the event manager

        Args:
            subcriber (Subscriber): Subscriber that subscribes to the event
        """
        self._subscribers.append(subcriber)

    def publish(self, event_type, payload):
        """
        publish the event to the notifiers

        Args:
            event_type (str): the type id of the event
            payload (dict): the message to be boardcasted with the event
        """
        for subsriber in self._subscribers:
            subsriber.handle(event_type, payload)
