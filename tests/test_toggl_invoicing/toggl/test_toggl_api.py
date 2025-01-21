import unittest
from unittest import mock
from toggl_invoicing.toggl import TogglApi
from tests.test_toggl_invoicing.toggl.mock_api import mocked_requests_get
from datetime import date, datetime
import logging


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


class ComponentDesignTests(unittest.TestCase):

    def test_api_response(self):
        time_entries_json = API.get_time_entries(
            start_date=date(2025, 1, 13), end_date=date(2025, 1, 19)
        )
        logging.info(f"Found {len(time_entries_json)} time entries")
        self.assertIsInstance(
            time_entries_json, list, msg="Time entries is a list of dictionaries"
        )
        for entry in time_entries_json:
            self.assertIsInstance(
                entry, dict, msg="Time entries is a list of dictionaries"
            )
            self.assertIsInstance(entry["id"], int, msg="Each entry has numeric ID")
            self.assertIsInstance(
                entry["project"], str, msg="'project' is string project name"
            )
            self.assertIsInstance(
                entry["description"],
                str,
                msg="'description' is detailed description of the task",
            )
            self.assertIsInstance(
                entry["start"],
                datetime,
                msg="'start' is a datetime object - start time of the entry",
            )
            self.assertIsInstance(
                entry["end"],
                datetime,
                msg="'end' is a datetime object  - end time of the entry",
            )
            self.assertGreater(
                entry["end"], entry["start"], msg="End time is greater than start time"
            )
            self.assertIsInstance(
                entry["duration"],
                int,
                msg="'duration' is the length of time entry in seconds",
            )
            self.assertEqual(
                entry["duration"],
                (entry["end"] - entry["start"]).seconds,
                msg="'duration' is consistent with 'start' and 'end' times",
            )
