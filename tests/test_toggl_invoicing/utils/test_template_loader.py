import unittest
from toggl_invoicing.utils.jinja import TemplateLoader
from jinja2 import Environment, Template
from jinja2.exceptions import TemplateNotFound
import tempfile
from uuid import uuid4
from unittest import mock

TEST_TEMPLATE = """
<html>
    <body>        
        <h1 id="title">Invoice no. {{ invoice_number }}</h1>
    </body>
</html>
"""


class ComponentDesignTests(unittest.TestCase):

    def test_read_from_filesystem(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(f"{tmpdir}/template.html", "w") as f:
                f.write(TEST_TEMPLATE)
            env = Environment(loader=TemplateLoader())
            template = env.get_template(f"{tmpdir}/template.html")
            self.assertIsInstance(
                template,
                Template,
                msg="TemplateLoader can load template from local file",
            )

    def test_read_from_url(self):
        env = Environment(loader=TemplateLoader())
        mock_request = mock.Mock()
        with mock.patch(
            "toggl_invoicing.toggl.toggl_api.requests.get", side_effect=mock_request
        ):
            mock_request.return_value.content = TEST_TEMPLATE.encode()
            template = env.get_template("http://www.acme.com/templates/template.html")
            self.assertIsInstance(
                template,
                Template,
                msg="TemplateLoader can load template from local file",
            )


class InputValidationTests(unittest.TestCase):
    def test_error_read_from_filesystem_file_not_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = Environment(loader=TemplateLoader())
            with self.assertRaises(
                TemplateNotFound,
                msg="TemplateLoader throws TemplateNotFound exception when template file does not exist",
            ):
                template = env.get_template(f"{tmpdir}/this_file_does_not_exist.html")

    def test_error_url_does_not_exist(self):
        env = Environment(loader=TemplateLoader())
        with self.assertRaises(
            TemplateNotFound,
            msg="TemplateLoader throws TemplateNotFound exception is template URL does not exist",
        ):
            template = env.get_template(
                f"http://www.{uuid4().hex}.com/this_url_does_not_exist.html"
            )
