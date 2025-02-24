from jinja2.loaders import FunctionLoader
from jinja2.exceptions import TemplateNotFound
import requests


def read_from_disc_or_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        try:
            template_request = requests.get(path)
            template_request.raise_for_status()
            return template_request.content.decode()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            raise TemplateNotFound(path)
    else:
        try:
            with open(path, "r") as f:
                template = f.read()
        except FileNotFoundError:
            raise TemplateNotFound(path)
    return template, None, None


class TemplateLoader(FunctionLoader):

    def __init__(self):
        super().__init__(load_func=read_from_disc_or_url)
