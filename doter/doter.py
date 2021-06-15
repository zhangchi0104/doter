from doter.events import EventPublisher


class DoterApp(EventPublisher):
    def __init__(self, config_path):
        f = open(path, 'r')

        config = load_yaml(f, Loader=FullLoader)
        f.close()