from cashcoach import secrets
import slackclient
import logging

import time
import sys
import logging

BOT_NAME = 'jarvis'
BOT_ID = u'U20NPAYG1'
# TODO: Store per user?
direct_channel = u'D20NK622Z'

logger = logging.getLogger("slack-api")

slack_client = slackclient.SlackClient(secrets.SLACK_TOKEN)


def send_message(message, channel=None):
    if channel is None:
        channel = direct_channel
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=message,
                          as_user=True)






