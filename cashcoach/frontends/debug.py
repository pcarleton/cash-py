import logging

from . import common

logger = logging.getLogger("frontend")


class DebugFrontend(common.Frontend):

    def send_message(self, message):
        logger.info("Sent message: %s", message)