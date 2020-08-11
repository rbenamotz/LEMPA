class Plugin(object):
    def __init__(self, app):
        self.app = app

    def on_start(self):
        pass

    def on_exit(self):
        pass

    def load_conf(self,conf):
        self.conf = conf

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__class__.__name__
