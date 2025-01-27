import unittest
from unittest import mock
from toggl_invoicing import TogglApi
from tests.test_toggl_invoicing.toggl.mock_api import mocked_requests_get
from datetime import date, datetime, timedelta
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
            if entry["end"] is not None:
                # entry["end"] is None if the entry is still running
                self.assertIsInstance(
                    entry["end"],
                    datetime,
                    msg="'end' is a datetime object  - end time of the entry",
                )
                self.assertGreater(
                    entry["end"],
                    entry["start"],
                    msg="End time is greater than start time",
                )
            self.assertIsInstance(
                entry["duration"],
                int,
                msg="'duration' is the length of time entry in seconds",
            )
            self.assertEqual(
                entry["duration"],
                (entry["end"].timestamp() if entry["end"] is not None else 0)
                - entry["start"].timestamp(),
                msg="'duration' is consistent with 'start' and 'end' times",
            )


class BoundaryCasesTests(unittest.TestCase):

    def test_end_date_is_included(self):
        start_date = date(2025, 1, 13)
        end_date = date(2025, 1, 18)
        time_entries = API.get_time_entries(start_date=start_date, end_date=end_date)
        self.assertLess(
            max([x["start"].date() for x in time_entries]),
            end_date + timedelta(days=1),
            msg="Entries starting after end_date are not included",
        )
        self.assertEqual(
            max([x["start"].date() for x in time_entries]),
            end_date,
            msg="Entries starting on the end date are included",
        )

    def test_running_entries_are_included(self):
        start_date = date(2025, 1, 13)
        end_date = date(2025, 1, 18)
        time_entries = API.get_time_entries(start_date=start_date, end_date=end_date)
        running_time_entries = [x for x in time_entries if x["end"] is None]
        self.assertGreater(len(running_time_entries), 0, msg="Running time entries")
        running_time_entry_example = running_time_entries[0]
        self.assertEqual(
            running_time_entry_example["duration"],
            -running_time_entry_example["start"].timestamp(),
            msg="Duration of running time entry is minus total start time, not the running duration",
        )
