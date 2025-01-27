import unittest
from unittest import mock
from toggl_invoicing.toggl import TogglApi
from tests.test_toggl_invoicing.toggl.mock_api import mocked_requests_get
from datetime import date, datetime
import logging
import os


def setUpModule():
    global API
    logging.basicConfig(level=logging.INFO)
    logging.info("Testing real API")
    if os.environ.get("API_TOKEN") is None:
        raise unittest.SkipTest(
            "Real API test ignored - set API_TOKEN environment variable to run the test."
        )
    API = TogglApi()


class ComponentDesignTests(unittest.TestCase):

    def test_api_response(self):
        start_date = date(2025, 1, 13)
        end_date = date(2025, 1, 19)
        time_entries_json = API.get_time_entries(
            start_date=start_date, end_date=end_date
        )
        if len(time_entries_json) == 0:
            raise unittest.SkipTest(
                f"No entries found between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}. Please adjust start and end date in the test to some valid values"
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
