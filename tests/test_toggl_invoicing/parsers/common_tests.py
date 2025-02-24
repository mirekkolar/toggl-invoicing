from datetime import date

TEST_INVOICE_METADATA = {
    "invoice_number": "20250001",
    "invoice_date": "2025/02/01",
    "invoice_due_date": "2025/02/14",
    "invoice_total": "$10,545.00",
    "contact_email": "wile.coyote@acme.com",
    "contact_phone": "123 456 789",
    "supplier_address": "Acme Corporation, Inc.\n177 Big Piece Rd\nFairfield, New Jersey\nUnited States",
    "subscriber_address": "Stark Industries\n800 Welch Rd\nPalo Alto, CA 94304\nUnited States",
    "bank_account": "ACCOUNT NUMBER: 8209008908\nSWIFT: USBKUS44XXX",
}


class ComponentDesignTests:

    def test_invoice_data_format(self):
        parser = self.parser
        invoice_data = parser.get_invoice_data(
            start_date=date(2025, 1, 1), end_date=date(2025, 1, 31)
        )
        self.assertIsInstance(
            invoice_data, dict, msg="Invoice data is parsed as dictionary"
        )
        # fmt: off
        mandatory_fields = [
            "invoice_number", "invoice_date", "invoice_due_date", "invoice_total",
            "contact_email", "contact_phone", "supplier_address", "subscriber_address",
            "bank_account", "items"
        ]        
        # fmt: on
        for mandatory_field in mandatory_fields:
            self.assertTrue(
                mandatory_field in invoice_data,
                msg=f"Invoice data should contain field '{mandatory_field}'",
            )
        invoice_items = invoice_data["items"]
        self.assertIsInstance(
            invoice_items, list, msg="'items' field is a list of objects"
        )
        for item in invoice_items:
            self.assertIsInstance(item, dict, msg="'items' field is a list of objects")
            mandatory_item_fields = ["description", "price", "quantity", "subtotal"]
            self.assertTrue(
                all([field in item for field in mandatory_item_fields]),
                msg=f"Each item should contain fields {', '.join(mandatory_item_fields)}",
            )
        return invoice_data
