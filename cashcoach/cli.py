import argparse
import logging
import sys

from cashcoach import backends, frontends
from cashcoach import bot
from cashcoach.spending import report
from cashcoach import secrets

logger = logging.getLogger(__name__)


def send_message(frontend, backend, message_name):
    logger.info("Getting message content...")
    all_messages = report.create_report(backend)

    if message_name not in all_messages:
        logger.error("Invalid message name %s", message_name)
        frontend.send_message("I couldn't find a message for %s" % message_name)
        return

    frontend.send_message(all_messages[message_name])


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s %(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stdout)

    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument('-m', "--message", type=str)
    parser.add_argument("--frontend", type=str, default="slack", choices=["slack", "commandline"])
    parser.add_argument("--backend", type=str)

    parser.add_argument("--flex", type=float)

    args = parser.parse_args()

    if args.command == 'dump':
        sheets = backends.SheetsBackend(secrets.SPREADSHEET_ID, secrets.CREDS_FILE_NAME)
        csv = backends.CsvBackend(args.backend, 0)

        csv.save_transactions(sheets.get_transactions())
        return

    if args.backend and 'csv' in args.backend:
        backend = backends.CsvBackend(args.backend, args.flex)
    else:
        backend = backends.SheetsBackend(secrets.SPREADSHEET_ID, secrets.CREDS_FILE_NAME)

    if args.frontend == "slack":
        frontend = frontends.SlackFrontend(secrets.DIRECT_CHANNEL)
    else:
        frontend = frontends.DebugFrontend()

    if args.command != 'bot':
        logger.warning("Unrecognized command %s", args.command)
        return

    mybot = bot.Bot(frontend, backend)
    if args.message:
        mybot.handle_message(args.message)
        return

    mybot.start()
