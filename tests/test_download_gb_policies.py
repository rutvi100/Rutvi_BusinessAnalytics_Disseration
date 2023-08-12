import unittest
import pandas as pd
import sys
import os
from pandas.testing import assert_frame_equal

sys.path.append(os.getcwd())

from src.scripts.download_gb_policies import get_gb_policies_status_date


class TestDownloadGBPolicies(unittest.TestCase):
    def test_get_gb_policies_status_date(self):
        class Test:
            def __init__(self, id, history_date, status, quote_id, debtor_id):
                self.id = id
                self.history_date = history_date
                self.status = status
                self.quote = Quote(quote_id, debtor_id)

        class Quote:
            def __init__(self, id, debtor_id):
                self.id = id
                self.transaction = Transaction(debtor_id)

        class Transaction:
            def __init__(self, debtor_id):
                self.debtor_id = debtor_id

        policy_list = [
            [
                Test(1, "2022-01-01", "Active", 1001, "ABC123"),
                Test(2, "2022-02-01", "Cancelled", 1002, "DEF456"),
                Test(3, "2022-03-01", "Active", 1003, "GHI789"),
            ],
            [
                Test(4, "2022-04-01", "Paid", 1004, "JKL012"),
                Test(5, "2022-05-01", "Active", 1005, "MNO345"),
            ],
            [
                Test(6, "2022-06-01", "Paid", 1006, "PQR678"),
            ],
        ]

        input_result = get_gb_policies_status_date(policy_list)

        expected_output = pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5, 6],
                "history_date": [
                    "2022-01-01",
                    "2022-02-01",
                    "2022-03-01",
                    "2022-04-01",
                    "2022-05-01",
                    "2022-06-01",
                ],
                "quote": [1001, 1002, 1003, 1004, 1005, 1006],
                "status": ["Active", "Cancelled", "Active", "Paid", "Active", "Paid"],
                "debtor_id": [
                    "ABC123",
                    "DEF456",
                    "GHI789",
                    "JKL012",
                    "MNO345",
                    "PQR678",
                ],
            }
        )

        assert_frame_equal(input_result, expected_output)
