from requests.exceptions import HTTPError


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code != 200:
                raise HTTPError(200, "Some error happened!")

    url = args[0]
    if url.split("/")[-1] == "projects":
        return MockResponse(
            status_code=200,
            json_data=[
                {"id": 1234, "workspace_id": 12345, "name": "project1"},
                {"id": 2345, "workspace_id": 12345, "name": "project2"},
                {"id": 3456, "workspace_id": 12345, "name": "family"},
            ],
        )
    elif url.split("/")[-1] == "time_entries":
        params = kwargs["params"]
        # fmt: off
        json_data = [
            {
                "id": 123456, "workspace_id": 12345, "project_id": 1234,
                "description": "Exploratory analysis",
                "start": "2025-01-14T08:15:23+00:00", "stop": "2025-01-14T12:54:02+00:00",
                "duration": 16719
            },
            {
                "id": 234567, "workspace_id": 12345, "project_id": 1234,
                "description": "Model development",
                "start": "2025-01-16T14:18:16+00:00", "stop": "2025-01-16T16:11:19+00:00",
                "duration": 6783
            },
            {
                "id": 345678, "workspace_id": 12345, "project_id": 2345,
                "description": "API design",
                "start": "2025-01-15T12:30:04+00:00", "stop": "2025-01-15T16:07:33+00:00",
                "duration": 13049
            },
            {
                "id": 456789, "workspace_id": 12345, "project_id": 1234,
                "description": "Model documentation",
                "start": "2025-01-17T09:02:11+00:00", "stop": None,
                "duration": -1737104531
            },
            {
                "id": 567890, "workspace_id": 12345, "project_id": 3456,
                "description": "Family lunch",
                "start": "2025-01-18T11:30:00+00:00", "stop": "2025-01-18T12:30:00+00:00",
                "duration": 3600,
            }
        ]
        # fmt: on
        json_data_filtered = [
            x
            for x in json_data
            if x["start"][:10] >= params["start_date"]
            and (True if x["stop"] is None else x["stop"][:10] < params["end_date"])
        ]
        return MockResponse(status_code=200, json_data=json_data_filtered)
    else:
        return MockResponse(status_code=404, json_data=None)
