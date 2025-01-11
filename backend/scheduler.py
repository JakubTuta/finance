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

            date_diff = 0

            if payment.next_payment_interval == "day":
                date_diff = payment.next_payment_interval_value

            elif payment.next_payment_interval == "week":
                date_diff = payment.next_payment_interval_value * 7

            elif payment.next_payment_interval == "month":
                date_month = payment.date.month + payment.next_payment_interval_value
                date_diff = (payment.date.replace(month=date_month) - payment.date).days

            if date_diff == 0:
                item_data = {
                    "name": payment.name,
                    "amount": payment.amount,
                    "date": payment.next_payment,
                    "category": payment.category,
                    "next_payment": None,
                    "next_payment_interval": None,
                    "next_payment_interval_value": None,
                }

            else:
                item_data = {
                    "name": payment.name,
                    "amount": payment.amount,
                    "date": payment.next_payment,
                    "category": payment.category,
                    "next_payment": payment.next_payment
                    + datetime.timedelta(days=date_diff),
                    "next_payment_interval": payment.next_payment_interval,
                    "next_payment_interval_value": payment.next_payment_interval_value,
                }

            self.wrapper.create_item(item_data)

        await asyncio.sleep(60 * 60 * 24)
