from . import common
from cashcoach.slack import api


class SlackFrontend(common.Frontend):

    def __init__(self, channel):
        self.channel = channel

    def send_message(self, message):
        api.send_message(message, self.channel)