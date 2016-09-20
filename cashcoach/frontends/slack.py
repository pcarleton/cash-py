from . import common
from cashcoach.slack import api

import time
import logging

logger = logging.getLogger(__name__)


class SlackFrontend(common.Frontend):

    def __init__(self, channel, delay=1):
        self.channel = channel
        self._delay = delay

    def send_message(self, message):
        api.send_message(message, self.channel)

    def serve(self, callback):

        if api.slack_client.rtm_connect():
            logger.info("Connected, running.")
            while True:
                command = self.parse_slack_output(api.slack_client.rtm_read())
                if command:
                    callback(command)

                time.sleep(self._delay)
        else:
            logger.warn('No connection')

    def parse_slack_output(self, slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                logger.debug(output)
                if (output and 'text' in output and  # and AT_BOT in output['text'] and
                            'channel' in output and output['channel'] == self.channel and
                            'user' in output and output['user'] != api.BOT_ID):
                    # return text after the @ mention, whitespace removed
                    logger.info("Got message from %s", output['user'])
                    return output['text'].strip().lower()
        return None