import argparse
import logging
import sys

from cashcoach.providers import bank
from cashcoach.backends import sheets
from cashcoach.slack import api, bot
from cashcoach.spending import report
from cashcoach import secrets

logger = logging.getLogger("main")


def update_transactions():
    """Fetch the latest transactions and store them"""
    logger.info("Pulling latest transactions.")
    latest_transactions = bank.get_new_spending()

    logger.info("Saving latest transactions.")
    backend = sheets.SheetsBackend(secrets.SPREADSHEET_NAME)
    backend.update_transactions(latest_transactions)


def run_bot():
    logger.info("Starting bot...")
    bot.serve()


def send_message(message_name):
    logger.info("Getting message content...")
    backend = sheets.SheetsBackend(secrets.SPREADSHEET_NAME)
    all_messages = report.create_report(backend)

    if message_name not in all_messages:
        logger.error("Invalid message name %s", message_name)
        api.send_message("I couldn't find a message for %s" % message_name)
        return

    api.send_message(all_messages[message_name])


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s %(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stdout)

    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument('-m', "--message", type=unicode)

    args = parser.parse_args()

    if args.command == 'update':
        update_transactions()
    elif args.command == 'bot':
        run_bot()
    elif args.command == 'message':
        send_message(args.message)
    else:
        logger.warning("Unrecognized command %s", args.command)
