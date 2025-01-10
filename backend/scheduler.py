import asyncio
import datetime
import typing

import main
from models import FinanceItem


class Scheduler:
    def __init__(self):
        self.wrapper = main.app.wrapper  # type: ignore

    def start(self):
        asyncio.create_task(self.create_new_payments())

    async def create_new_payments(self):
        today_payments: typing.AsyncGenerator[FinanceItem, None] = (
            self.wrapper.list_next_payments()
        )

        async for payment in today_payments:
            if payment.next_payment is None:
                continue

            date_diff = payment.next_payment - payment.date
            date_diff_in_days = date_diff.days

            item_data = {
                "name": payment.name,
                "amount": payment.amount,
                "date": payment.next_payment,
                "category": payment.category,
                "next_payment": payment.next_payment
                + datetime.timedelta(days=date_diff_in_days),
            }

            self.wrapper.create_item(item_data)

        await asyncio.sleep(60 * 60 * 24)
