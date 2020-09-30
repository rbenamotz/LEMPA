
class Programmer(object):
    def __init__(self, app, profile):
        self.app = app
        self.profile = profile
        self.comm_speed = 125000
        if "speed" in self.profile:
            self.comm_speed = self.profile["speed"]

    def program(self):
        pass

    def erase(self):
        raise Exception("Erase not supported. Maybe nuke the device?")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__class__.__name__
