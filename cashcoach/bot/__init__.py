from cashcoach.spending import report


class Bot(object):

    def __init__(self, frontend, backend):
        self.frontend = frontend
        self.backend = backend

    def start(self):
        self.frontend.serve(self.handle_message)

    def handle_message(self, message):
        if 'last' in message:
            response = report.last_n(self.backend)
        else:
            response = "Not sure what to do with that."
        self.frontend.send_message(response)