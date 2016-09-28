

class Frontend(object):

    def send_message(self, message):
        raise NotImplementedError()

    def serve(self, callback):
        raise NotImplementedError()
