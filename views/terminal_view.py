from views.view import View


class TerminalView(View):
    def __init__(self, app):
        super().__init__(app)

    def cleanup(self):
        print("Goodbye")

    def print(self, txt):
        print(txt)
  
    def detail(self, txt):
        print(txt)


    def error(self, e):
        print('\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print(e)
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n')

    def header(self):
        print('\n\n==========================================================================')
        print(self.app.app_state)
        print('==========================================================================')
