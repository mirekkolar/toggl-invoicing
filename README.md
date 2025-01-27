# Toggl Invoicing

Tools for automatic summaries and invoicing from [Toggl](https://toggl.com/)

## Installation

Install package with pip

```
pip install git+https://github.com/mirekkolar/toggl-invoicing.git
```

Unittests run against mock API, so you can run them even without Toggl account
```
python -m unittest discover tests -v
```

You can also run tests against real Toggl API; for this you need to set `TOGGL_API_TOKEN` environment variable to your Toggl API token (see [usage](#api-token-authentication)).
```
python -m unittest discover tests -p "_test*.py" -v
```

## Usage

### <a id = "api-token-authentication"></a> API Token authentication

Package reads data from Toggl API using [API token](https://engineering.toggl.com/docs/authentication/#http-basic-auth-with-api-token), which must be provided
1. as environment variable `TOGGL_API_TOKEN` (this is the recommended approach). We are using [python-dotenv](https://pypi.org/project/python-dotenv/), so you can declare this variable in your projects's .env file
```
from toggl_invoicing import TogglApi

API = TogglApi()
```
2. or directly through `TOGGL_API_TOKEN` parameter of `TogglApi` class
```
API = TogglApi(TOGGL_API_TOKEN="mysupersecrettoken")
```

Toggl API URL is set to `https://api.track.toggl.com/api/v9`

### Getting time entries

In order to get your time entries within specified period, use `get_time_entries` method with `datetime.date` objects as `start_date` and `end_date` arguments.
```
from datetime import date

time_entries = API.get_time_entries(
    start_date=date(2025, 1, 13), end_date=date(2025, 1, 19)
)
```
API response is list of dictionary objects
```
{
    "id": 123456,
    "project": "project1",
    "description": "Exploratory analysis",
    "start": datetime.datetime(2025, 1, 16, 8, 15, 23, tzinfo=datetime.timezone.utc),
    "end": datetime.datetime(2025, 1, 16, 12, 54, 2, tzinfo=datetime.timezone.utc),
    "duration": 16719
}
```

### Decent API usage

The simple client doesn't handle [Toggl's general response logic](https://engineering.toggl.com/docs/#generic-responses), so make sure that your application doesn't retry indefinitely if there is HTTPError on the client.