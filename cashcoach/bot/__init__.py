from cashcoach.spending import report
import logging

logger = logging.getLogger(__name__)


class Bot(object):

    def __init__(self, frontend, backend):
        self.frontend = frontend
        self.backend = backend
        self.state = None

    def start(self):
        self.frontend.serve(self.handle_message)

    def last_n(self, message):
        new_page = None
        if "prev" in message:
            page = self.state['page']
            new_page = page + 1
        elif "next" in message:
            page = self.state['page']

            if page == 0:
                self.frontend.send_message("Already at latest.")
                return True
            new_page = page - 1
        if new_page:
            response, context = report.last_n(self.backend, page=new_page)
            self.state = {"action": self.last_n, "context": context, "page": new_page}
            self.frontend.send_message(response)
            return True

        pieces = message.strip().split()

        try:
            tnums = map(int, pieces)
        except ValueError:
            return False

        self.frontend.send_message(
            "Excluding #'s {} ...".format(", ".join(map(str, tnums))))

        transaction_ids = [self.state['context'][tnum] for tnum in tnums]

        self.backend.exclude_transactions(transaction_ids)
        return True

    def handle_message(self, message):
        if self.state is not None:
            logger.info(self.state)
            if self.state['action'](message):
                return True

        messages = ['month', 'weekly', 'adjusted',
                    'lastweek', 'lastmonth']

        target_m = next((m for m in messages if m in message),
                        None)

        if target_m:
            all_messages = report.create_report(self.backend)
            response = all_messages[target_m]
        elif 'summary' in message:
            msgs = report.create_summary(self.backend)
            response = "\n".join(msgs)
        elif 'last' in message:
            response, context = report.last_n(self.backend, page=0)
            self.state = {"action": self.last_n, "context": context, "page": 0}
        else:
            response = "Not sure what to do with that."
        self.frontend.send_message(response)
        return True