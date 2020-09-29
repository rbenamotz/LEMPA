class Programmer(object):
    def __init__(self, app, profile):
        self.app = app
        self.profile = profile
        self.programming_speed = 125000
        if "speed" in self.profile:
            self.programming_speed = self.profile["speed"]

    def program(self):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__class__.__name__
