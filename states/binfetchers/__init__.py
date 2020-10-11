class BinFetcher(object):
    def __init__(self, app):
        self.app = app

    def __fetch_impl__(self, bin_info, bin_file):
        raise Exception("BIN fetch mechanism not implemented")

    def fetch(self, b):
        name = b["name"]
        bin_file = "./bins/%s.hex" % (name)
        return self.__fetch_impl__(b, bin_file)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__class__.__name__
