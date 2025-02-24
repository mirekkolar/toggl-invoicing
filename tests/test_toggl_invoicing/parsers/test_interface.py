import unittest
from toggl_invoicing.parsers.abstract_template_data_parser import (
    AbstractTemplateDataParser,
)
from tests.test_toggl_invoicing.parsers.common_tests import (
    TEST_INVOICE_METADATA,
    ComponentDesignTests as ComponentDesignCommonTests,
)
from toggl_invoicing import TogglApi
from tests.test_toggl_invoicing.toggl.mock_api import mocked_requests_get
from datetime import date
import logging
from unittest import mock


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


class DummyTemplateDataParser(AbstractTemplateDataParser):
    def get_invoice_data(self, start_date: date, end_date: date):
        return super().get_invoice_data(start_date, end_date)


class ComponentDesignTests(unittest.TestCase, ComponentDesignCommonTests):

    def setUp(self):
        self.parser = DummyTemplateDataParser(**TEST_INVOICE_METADATA)

    def test_invoice_data_format(self):
        super().test_invoice_data_format(
            start_date=date(2025, 1, 1), end_date=date(2025, 1, 31)
        )
