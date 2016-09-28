from cashcoach import secrets
import slackclient

BOT_NAME = 'jarvis'
BOT_ID = u'U20NPAYG1'

slack_client = slackclient.SlackClient(secrets.SLACK_TOKEN)


def send_message(message, channel):
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=message,
                          as_user=True)






