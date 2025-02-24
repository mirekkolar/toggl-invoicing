from abc import ABC, abstractmethod
from datetime import date


class AbstractTemplateDataParser(ABC):

    def __init__(
        self,
        invoice_number: str | int,
        invoice_date: str,
        invoice_due_date: str,
        invoice_total: float,
        contact_email: str,
        contact_phone: str,
        supplier_address: str,
        subscriber_address: str,
        bank_account: str,
        **kwargs,
    ):
        self.invoice_metadata = {
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "invoice_due_date": invoice_due_date,
            "invoice_total": invoice_total,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "supplier_address": supplier_address,
            "subscriber_address": subscriber_address,
            "bank_account": bank_account,
        }

    @abstractmethod
    def get_invoice_data(self, start_date: date, end_date: date) -> dict:
        invoice_metadata = self.invoice_metadata
        invoice_data = {
            **invoice_metadata,
            "invoice_description": "We're invoicing your for services provided during 2025/01/01 - 2025/01/31",
            "purpose_of_payment": "Purpose of payment:\n/BUSINESS/SERVICE TRADE",
            "items": [
                {
                    "description": "Website design",
                    "price": "$34.20",
                    "amount": "100",
                    "subtotal": "$3,420.00",
                },
                {
                    "description": "Website development",
                    "price": "$45.50",
                    "amount": "100",
                    "subtotal": "$4,550.00",
                },
                {
                    "description": "Website integration",
                    "price": "$25.75",
                    "amount": "100",
                    "subtotal": "$2,575.00",
                },
            ],
        }
        return invoice_data
