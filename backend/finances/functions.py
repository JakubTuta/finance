import datetime
import os
import typing

import helpers.database as database
import pydantic
import requests
from helpers.currencies import currencies
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from . import models


def is_model_subscription(
    item: typing.Union[models.FinanceItem, models.SubscriptionItem],
) -> bool:
    return (
        isinstance(item, models.SubscriptionItem)
        and item.repeat_period is not None
        and item.repeat_value is not None
    )


langchain_template = (
    "You are tasked with extracting specific information about payments from the CSV file: {file_content}. "
    "Format the response in this JSON format: {format_instructions}. "
    "Please follow these instructions carefully: \n\n"
    "1. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "2. **Empty Response:** If no information matches the description, return an empty string ('')."
    "3. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

categories = [
    "entertainment",
    "food",
    "groceries",
    "payment",
    "others",
]


class BotResponse(pydantic.BaseModel):
    title: str = pydantic.Field(
        description="The title of the payment readable for the user."
    )
    amount: float = pydantic.Field(description="The amount of the payment.")
    currency: str = pydantic.Field(description="The currency of the payment.")
    date: str = pydantic.Field(description="Full date of the payment in ISO standard.")
    category: str = pydantic.Field(
        description=f"The category of the content. Choose one from the list: [{', '.join(categories)}]"
    )


class BotResponseList(pydantic.BaseModel):
    items: typing.List[BotResponse] = pydantic.Field(
        description="List of payment items"
    )


def ask_bot(content: typing.List[str]) -> typing.List[BotResponse]:
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    model = ChatGoogleGenerativeAI(
        api_key=api_key,  # type: ignore
        model="gemini-2.0-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    parser = JsonOutputParser(pydantic_object=BotResponseList)

    prompt = PromptTemplate(
        template=langchain_template,
        input_variables=["file_content"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    response = chain.invoke({"file_content": content})

    response_list = BotResponseList(items=response["items"])

    for item in response_list.items:
        if item.category.lower() in categories:
            item.category = item.category.lower()
        else:
            item.category = "others"

    return response_list.items


async def update_currency_rates():
    collection = database.get_collection("currency_rates")

    date_doc_id = "update_date"
    date_doc = await collection.find_one({"_id": date_doc_id})

    if date_doc is None:
        await collection.insert_one(
            {"_id": date_doc_id, "date": datetime.datetime.now()}
        )
        last_update_time = datetime.datetime.now()
    else:
        last_update_time = date_doc["date"]

    if datetime.datetime.now() - last_update_time < datetime.timedelta(days=1):
        return

    api_key = os.environ.get("CURRENCY_API_KEY")
    if not api_key:
        raise ValueError("CURRENCY_API_KEY environment variable is not set.")

    data = {}
    for currency in currencies:
        other_currencies = currencies.copy()
        other_currencies.remove(currency)
        other_currencies_str = ",".join(other_currencies)

        url = f"https://api.freecurrencyapi.com/v1/latest?apikey={api_key}&base_currency={currency}&currencies={other_currencies_str}"

        response = requests.get(url)

        data[currency] = response.json()["data"]

    await collection.update_one(
        {"_id": date_doc_id},
        {"$set": {"date": datetime.datetime.now()}},
        upsert=True,
    )

    for base_currency, rates in data.items():
        await collection.update_one(
            {"_id": base_currency}, {"$set": rates}, upsert=True
        )


async def get_currency_rates():
    collection = database.get_collection("currency_rates")

    rates_per_currency = {}

    for currency in currencies:
        rates = await collection.find_one({"_id": currency})

        if rates is not None:
            del rates["_id"]
            rates_per_currency[currency] = rates

    return rates_per_currency
