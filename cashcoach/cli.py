import argparse
import logging
import sys

from cashcoach.providers import bank
from cashcoach import backends
from cashcoach.slack import api, bot
from cashcoach.spending import report
from cashcoach import secrets

logger = logging.getLogger("main")


def update_transactions(backend):
    """Fetch the latest transactions and store them"""
    logger.info("Pulling latest transactions.")
    latest_transactions = bank.get_new_spending()

    logger.info("Saving latest transactions.")
    backend.update_transactions(latest_transactions)


def run_bot():
    logger.info("Starting bot...")
    bot.serve()


def send_message(backend, message_name, silent=False):
    logger.info("Getting message content...")
    all_messages = report.create_report(backend)

    if message_name not in all_messages:
        logger.error("Invalid message name %s", message_name)
        api.send_message("I couldn't find a message for %s" % message_name)
        return

    if not silent:
        api.send_message(all_messages[message_name])
    else:
        logger.info(all_messages[message_name])


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s %(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stdout)

    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument('-m', "--message", type=unicode)
    parser.add_argument("--silent", action='store_true')
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

    if args.command == 'update':
        update_transactions(backend)
    elif args.command == 'bot':
        run_bot()
    elif args.command == 'message':
        send_message(backend, args.message, args.silent)
    else:
        logger.warning("Unrecognized command %s", args.command)
