import argparse
import logging
import sys

from providers import bank

logger = logging.getLogger("main")


def update_transactions():
    """Fetch the latest transactions and store them"""

    bank.update_spending()




def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(name)s %(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stdout)

    parser = argparse.ArgumentParser()
    parser.add_argument("command")

    args = parser.parse_args()

    if args.command == 'update':
        update_transactions()
        return

    logger.warning("Unrecognized command %s", args.command)
