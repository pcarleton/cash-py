import logging

from . import common

logger = logging.getLogger(__name__)


class DebugFrontend(common.Frontend):

    def send_message(self, message):
        logger.info("Sent message: %s", message)