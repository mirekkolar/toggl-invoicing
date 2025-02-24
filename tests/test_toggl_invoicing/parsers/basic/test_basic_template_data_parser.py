import unittest
from toggl_invoicing.parsers import BasicTemplateDataParser
from tests.test_toggl_invoicing.parsers.common_tests import (
    TEST_INVOICE_METADATA,
    ComponentDesignTests as ComponentDesignCommonTests,
)
from toggl_invoicing import TogglApi
from tests.test_toggl_invoicing.toggl.mock_api import mocked_requests_get
import logging
from unittest import mock
from datetime import date
import pandas as pd


def setUpModule():
    global API, api_mock
    logging.basicConfig(level=logging.INFO)
    logging.info("Testing mock API")
    API = TogglApi(api_url="http://api.mock.com", api_token="mysupersecrettoken")
    api_mock = mock.patch(
        "toggl_invoicing.toggl.toggl_api.requests.get", side_effect=mocked_requests_get
    )
    api_mock.start()


def tearDownModule():
    api_mock.stop()


def parse_number(x: str) -> float:
    return float(x.replace(",", ""))


class ComponentDesignTests(unittest.TestCase, ComponentDesignCommonTests):

    def setUp(self):
        self.parser = BasicTemplateDataParser(
            project="project1", unit_price=1500, **TEST_INVOICE_METADATA
        )

    def test_invoice_data_format(self):
        invoice_data = super().test_invoice_data_format(
            start_date=date(2025, 1, 1), end_date=date(2025, 1, 31)
        )
        # fmt: off
        invoice_fields = [
            # common mandatory fields
            "invoice_number", "invoice_date", "invoice_due_date", "invoice_total",
            "contact_email", "contact_phone", "supplier_address", "subscriber_address",
            "bank_account", "items",
            # specific fields in this parser
            "invoice_description", "purpose_of_payment",
        ] 
        # fmt: on
        self.assertSetEqual(
            set(invoice_fields),
            set(invoice_data.keys()),
            msg="Basic template data has expected fields",
        )
        self.assertEqual(
            invoice_data["invoice_description"],
            f"We're invoicing your for services provided during period {date(2025, 1, 1).strftime('%Y/%m/%d')} - {date(2025, 1, 31).strftime('%Y/%m/%d')}",
        )
        self.assertEqual(
            invoice_data["purpose_of_payment"],
            "Purpose of payment:\n/BUSINESS/SERVICE TRADE",
        )


class ComputationTests(unittest.TestCase):

    def setUp(self):
        self.parser = BasicTemplateDataParser(
            project="project1", unit_price=1500, **TEST_INVOICE_METADATA
        )

    def test_subtotals(self):
        parser = self.parser
        invoice_data = parser.get_invoice_data(
            start_date=date(2025, 1, 1), end_date=date(2025, 1, 31)
        )
        invoice_total = parse_number(invoice_data["invoice_total"])
        invoice_items = pd.DataFrame(invoice_data["items"]).assign(
            price=lambda df: df["price"].apply(parse_number),
            amount=lambda df: df["amount"].apply(parse_number),
            subtotal=lambda df: df["subtotal"].apply(parse_number),
        )
        self.assertSetEqual(
            set(invoice_items["price"]),
            {1500},
            msg="Unit price of all items corresponds to price parameter",
        )
        self.assertTrue(
            all(
                invoice_items["subtotal"]
                == invoice_items["price"] * invoice_items["amount"]
            ),
            msg="Item subtotals equal to price times amount",
        )
        self.assertEqual(
            invoice_items["subtotal"].sum(),
            invoice_total,
            msg="Invoice total equals sum of item subtotals",
        )
        self.assertTrue(
            all(invoice_items["amount"] == invoice_items["amount"].round()),
            msg="Item amounts are rounded to full hour",
        )
