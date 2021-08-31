from views import View
HEADER_LEN = 70


class TerminalView(View):
    def __init__(self, app):
        super().__init__(app)

    def cleanup(self):
        print("Goodbye")

    def print(self, txt):
        if (txt):
            print("\033[92m{}\033[39m".format(txt))

    def detail(self, txt):
        print(txt)

    def error(self, e):
        if not e:
            return
        print("\n\n{}".format("|" * HEADER_LEN))
        print("\033[31m{}\033[39m".format(e))
        print("!" * HEADER_LEN)

    def header(self):
        if self.app and self.app.app_state:
            print("\n\n\033[7m{:^{w}}\033[0m".format(self.app.app_state, w=HEADER_LEN))
