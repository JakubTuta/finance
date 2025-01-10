import threading
import time

import main


class Scheduler:
    def __init__(self):
        self.wrapper = main.app.wrapper  # type: ignore
        self.threads = {}

        self.create_new_payments()

    def create_new_payments(self):
        def wrapper():
            today_payments = self.wrapper.list_next_payments()

            for payment in today_payments:
                date_diff = payment.next_payment - payment.date
                date_diff_in_days = date_diff.days

                item_data = {
                    "name": payment.name,
                    "amount": payment.amount,
                    "date": payment.next_payment,
                    "category": payment.category,
                    "next_payment": payment.next_payment + date_diff_in_days,
                }

                self.wrapper.create_item(item_data)

            time.sleep(60 * 60 * 24)

        thread = threading.Thread(target=wrapper)
        thread.daemon = True
        thread.start()

        self.threads["create_new_payments"] = thread
