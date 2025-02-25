from toggl_invoicing.parsers.abstract_template_data_parser import (
    AbstractTemplateDataParser,
)
from datetime import date
from toggl_invoicing import TogglApi
import pandas as pd
import numpy as np
from typing import Callable


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
        invoice_description_func: Callable[
            [date, date, dict], str
        ] = lambda start_date, end_date, invoice_metadata: "",
        purpose_of_payment_func: Callable[[dict], str] = lambda invoice_metadata: "",
        price_format: Callable[[float], str] = lambda x: f"{x:,.2f}",
        **kwargs,
    ):
        self.project = project
        self.unit_price = unit_price
        self.invoice_description_func = invoice_description_func
        self.purpose_of_payment_func = purpose_of_payment_func
        self.price_format = price_format
        self.invoice_metadata = {
            **{
                "project": project,
                "unit_price": unit_price,
                "invoice_number": invoice_number,
                "invoice_date": invoice_date,
                "invoice_due_date": invoice_due_date,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "supplier_address": supplier_address,
                "subscriber_address": subscriber_address,
                "bank_account": bank_account,
            },
            **kwargs,
        }

    def get_invoice_data(self, start_date: date, end_date: date) -> dict:
        invoice_description = self.invoice_description_func(
            start_date, end_date, self.invoice_metadata
        )
        purpose_of_payment = self.purpose_of_payment_func(self.invoice_metadata)
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
        invoice_total = self.price_format(parsed_time_entries["subtotal"].sum())
        parsed_time_entries["price"] = self.price_format(self.unit_price)
        parsed_time_entries["amount"] = (
            parsed_time_entries["duration_rounded"].astype("int").astype("str")
        )
        items = (
            parsed_time_entries[["description", "price", "amount", "subtotal"]]
            .assign(subtotal=lambda df: df["subtotal"].apply(self.price_format))
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
