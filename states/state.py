class State(object):
    def __init__(self, app):
        self.app = app

    def on_event(self, event):
        return self

    def do_step(self):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__class__.__name__
