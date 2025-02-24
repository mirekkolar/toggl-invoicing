from toggl_invoicing.parsers.abstract_template_data_parser import (
    AbstractTemplateDataParser,
)
from datetime import date
from toggl_invoicing import TogglApi
import pandas as pd
import numpy as np


def round_vector(x: pd.Series) -> pd.Series:
    total = round(x.sum())
    base = np.floor(x)
    decimal = x - base
    to_add = total - base.sum()
    min_rank_to_add = len(x) - to_add + 1
    add_integer = pd.Series(index=x.index, data=1).where(
        decimal.rank() >= min_rank_to_add, other=0
    )
    return base + add_integer


def price_format(x: float) -> str:
    return f"{x:,}"


class BasicTemplateDataParser(AbstractTemplateDataParser):

    def __init__(
        self,
        project: str,
        unit_price: float,
        invoice_number: str | int,
        invoice_date: str,
        invoice_due_date: str,
        contact_email: str,
        contact_phone: str,
        supplier_address: str,
        subscriber_address: str,
        bank_account: str,
        **kwargs,
    ):
        self.project = project
        self.unit_price = unit_price
        self.invoice_metadata = {
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "invoice_due_date": invoice_due_date,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "supplier_address": supplier_address,
            "subscriber_address": subscriber_address,
            "bank_account": bank_account,
        }

    def get_invoice_data(self, start_date: date, end_date: date) -> dict:
        invoice_description = f"We're invoicing your for services provided during period {start_date.strftime('%Y/%m/%d')} - {end_date.strftime('%Y/%m/%d')}"
        purpose_of_payment = "Purpose of payment:\n/BUSINESS/SERVICE TRADE"
        time_entries = TogglApi().get_time_entries(
            start_date=start_date, end_date=end_date
        )
        parsed_time_entries = (
            pd.DataFrame(
                columns=["description", "duration"],
                data=[
                    [time_entry["description"], time_entry["duration"]]
                    # time entry is not None should be removed once we ensure the unended time entries are truncated to datetime.now()
                    for time_entry in time_entries
                    if time_entry["project"] == self.project
                    and time_entry["end"] is not None
                ],
            )
            .groupby("description")["duration"]
            .sum()
            .reset_index()
        )
        parsed_time_entries["duration_hours"] = parsed_time_entries["duration"] / 3600
        parsed_time_entries["duration_rounded"] = round_vector(
            parsed_time_entries["duration_hours"]
        )
        parsed_time_entries["subtotal"] = (
            parsed_time_entries["duration_rounded"] * self.unit_price
        )
        invoice_total = price_format(parsed_time_entries["subtotal"].sum())
        parsed_time_entries["price"] = price_format(self.unit_price)
        parsed_time_entries["amount"] = (
            parsed_time_entries["duration_rounded"].astype("int").astype("str")
        )
        items = (
            parsed_time_entries[["description", "price", "amount", "subtotal"]]
            .assign(subtotal=lambda df: df["subtotal"].apply(price_format))
            .to_dict(orient="records")
        )
        return {
            **self.invoice_metadata,
            **{
                "invoice_total": invoice_total,
                "invoice_description": invoice_description,
                "purpose_of_payment": purpose_of_payment,
                "items": items,
            },
        }
