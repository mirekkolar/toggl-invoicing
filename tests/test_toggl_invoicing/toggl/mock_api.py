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
    if url == "http://api.mock.com/me/projects":
        return MockResponse(
            status_code=200,
            json_data=[
                {"id": 1234, "workspace_id": 12345, "name": "project1"},
                {"id": 2345, "workspace_id": 12345, "name": "project2"},
            ],
        )
    elif url == "http://api.mock.com/me/time_entries":
        return MockResponse(
            status_code=200,
            # fmt: off
            json_data = [
                {
                    "id": 123456, "workspace_id": 12345, "project_id": 1234,
                    "description": "Exploratory analysis",
                    "start": "2025-01-16T08:15:23+00:00", "stop": "2025-01-16T12:54:02+00:00",
                    "duration": 16719
                },
                {
                    "id": 234567, "workspace_id": 12345, "project_id": 1234,
                    "description": "Model development",
                    "start": "2025-01-18T14:18:16+00:00", "stop": "2025-01-18T16:11:19+00:00",
                    "duration": 6783
                },
                {
                    "id": 234567, "workspace_id": 12345, "project_id": 2345,
                    "description": "API design",
                    "start": "2025-01-15T12:30:04+00:00", "stop": "2025-01-15T16:07:33+00:00",
                    "duration": 13049
                },
            ]
            # fmt: on
        )
    else:
        return MockResponse(status_code=404, json_data=None)
