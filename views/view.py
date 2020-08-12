class View(object):
    def __init__(self, app):
        self.app = app

    def header(self):
        pass

    def print(self, txt):
        pass

    def error(self, e):
        pass

    def cleanup(self):
        pass

    def refresh(self):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__class__.__name__
