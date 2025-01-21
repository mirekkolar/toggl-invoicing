from typing import Optional, List
import requests
from requests.auth import HTTPBasicAuth
import os
from datetime import datetime, date
import logging

API_URL = "https://api.track.toggl.com/api/v9"


class TogglApi:

    def __init__(self, api_token: Optional[str] = None, api_url: Optional[str] = None):
        api_token = api_token if api_token is not None else os.environ["API_TOKEN"]
        self.auth = HTTPBasicAuth(api_token, "api_token")
        self.api_url = api_url if api_url is not None else API_URL

    def _call(self, endpoint: str, **kwargs) -> requests.models.Response:
        # ensuring content-type is set as per https://engineering.toggl.com/docs/#the-api-format
        headers = {**kwargs.get("headers", {}), **{"Content-Type": "application/json"}}
        response = requests.get(
            f"{self.api_url}{endpoint}", headers=headers, auth=self.auth, **kwargs
        )
        return response

    def get_time_entries(self, start_date: date, end_date: date) -> List[dict]:
        logging.info(f"Fetching project names..")
        projects_call = self._call("/me/projects")
        projects_call.raise_for_status()
        projects = projects_call.json()
        project_mapping = {project["id"]: project["name"] for project in projects}
        logging.info(f"Project names prepared")
        logging.info(f"Fetching time entries..")
        time_entries_call = self._call(
            f"/me/time_entries",
            params={
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            },
        )
        time_entries_call.raise_for_status()
        time_entries = [
            {
                "id": entry["id"],
                "project": project_mapping[entry["project_id"]],
                "description": entry["description"],
                "start": datetime.fromisoformat(entry["start"]),
                "end": datetime.fromisoformat(entry["stop"]),
                "duration": entry["duration"],
            }
            for entry in time_entries_call.json()
        ]
        return time_entries
