import logging
import time
import gsheets

from cashcoach.slack import api as slack_api
from cashcoach.providers import bank
from cashcoach.spending import report


logger = logging.getLogger("bot")

# TODO: Generate
sheet_link = u"https://docs.google.com/spreadsheets/d/1s_imsHhZuC-iDX3R0I0s2rN2uFjaWB6UXrenjf7rnVg/edit#gid=0"


def serve(delay=1):
    if slack_api.slack_client.rtm_connect():
        logger.info("Connected, running.")
        while True:
            command, channel = parse_slack_output(slack_api.slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)

            time.sleep(delay)
    else:
        logger.warn('No connection')


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            logger.debug(output)
#             if 'channel' in output and output['channel'] == direct_channel:
#                 return output['text'], output['channel']
            if (output and 'text' in output and # and AT_BOT in output['text'] and
                'channel' in output and output['channel'] == slack_api.direct_channel and
               'user' in output and output['user'] != slack_api.BOT_ID):
                # return text after the @ mention, whitespace removed
                logger.info("Got message from %s", output['user'])
                return output['text'].strip().lower(), output['channel']
    return None, None


def handle_command(command, channel):
    def _respond(msg):
        logger.debug("Responding in %s", channel)
        slack_api.send_message(msg, channel)

    try:
        if command.startswith("balance"):
            response = "Don't have that info."
            _respond(response)

        elif 'sheet' in command:
            _respond(sheet_link)
        elif 'update' in command:
            _respond("Updating spending ...")
            bank.update_spending()
            _respond("Sheet updated: %s" % sheet_link)
        elif 'report' in command:
            _respond("I'm on it!")
            logger.debug("Fetching spreadsheet")
            ss = gsheets.get_spreadsheet("Summer 2016 Budget")

            logger.debug("Making report")
            msgs = report.create_report(ss)

            _respond(msgs['month'])

            _respond(msgs['adjusted'])
            logger.debug("Sent messages.")
        else:
            _respond("Unrecognized command.")
    except Exception as e:
        logger.error(e)
        _respond("Uh-oh... I had an error.")