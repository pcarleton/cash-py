import argparse
import logging
import sys

from cashcoach.providers import bank
from cashcoach import backends, frontends
# from cashcoach.slack import bot
from cashcoach import bot
from cashcoach.spending import report
from cashcoach import secrets

logger = logging.getLogger(__name__)


def update_transactions(backend):
    """Fetch the latest transactions and store them"""
    logger.info("Pulling latest transactions.")
    latest_transactions = bank.get_new_spending()

    logger.info("Saving latest transactions.")
    backend.update_transactions(latest_transactions)


# def run_bot():
#     logger.info("Starting bot...")
#     bot.serve()


def send_message(frontend, backend, message_name):
    logger.info("Getting message content...")
    all_messages = report.create_report(backend)

    if message_name not in all_messages:
        logger.error("Invalid message name %s", message_name)
        frontend.send_message("I couldn't find a message for %s" % message_name)
        return

    frontend.send_message(all_messages[message_name])


def send_last_n(frontend, backend):
    msg = report.last_n(backend)
    frontend.send_message(msg)


def send_summary(frontend, backend):
    msgs = report.create_summary(backend)
    frontend.send_message("\n".join(msgs))


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s %(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stdout)

    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument('-m', "--message", type=unicode)
    parser.add_argument("--frontend", type=unicode, default="slack")
    parser.add_argument("--backend", type=unicode)
    parser.add_argument("--flex", type=float)

    args = parser.parse_args()

    if args.command == 'dump':
        sheets = backends.SheetsBackend(secrets.SPREADSHEET_NAME)
        csv = backends.CsvBackend(args.backend, 0)

        csv.save_transactions(sheets.get_transactions())
        return

    if args.backend and 'csv' in args.backend:
        backend = backends.CsvBackend(args.backend, args.flex)
    else:
        backend = backends.SheetsBackend(secrets.SPREADSHEET_NAME)

    if args.frontend == "slack":
        frontend = frontends.SlackFrontend(secrets.DIRECT_CHANNEL)
    else:
        frontend = frontends.DebugFrontend()

    if args.command == 'update':
        update_transactions(backend)
    elif args.command == 'bot':
        mybot = bot.Bot(frontend, backend)
        mybot.start()
    elif args.command == 'message':
        send_message(frontend, backend, args.message)
    elif args.command == 'summary':
        send_summary(frontend, backend)
    else:
        logger.warning("Unrecognized command %s", args.command)
