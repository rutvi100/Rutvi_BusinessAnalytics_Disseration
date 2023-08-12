import os
import sys
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

sys.path.append(os.getcwd())

import logging

from src.scripts.label_gb_policies import (
    drop_policy_rows_if_ever_status,
    drop_rows_by_current_status_dates,
    drop_rows_by_status,
    filter_not_collectable,
    get_policy_status,
    label_policies_using_status,
)

logger = logging.basicConfig(level=logging.INFO)


class TestMapLabelGBPolicies(unittest.TestCase):
    def test_label_policies_using_status(self):
        input_data = pd.DataFrame(
            {"id": ["1", "2", "3"], "status": ["paid", "late", "under_collection"]}
        )
        label_policies_using_status(input_data, logger)

        expected_output = pd.DataFrame(
            {
                "id": ["1", "2", "3"],
                "status": ["paid", "late", "under_collection"],
                "mapped_status": ["paid", "late", "under_collection"],
                "label": [0, 0, 1],
            }
        )
        assert_frame_equal(input_data, expected_output)

    def test_filter_not_collectable(self):
        input_data = pd.DataFrame(
            {
                "id": ["1", "1", "2", "3", "4"],
                "status": [
                    "late",
                    "not_collectable",
                    "late",
                    "not_collectable",
                    "paid",
                ],
                "history_date": [
                    "2021-10-28",
                    "2021-12-31",
                    "2022-01-02",
                    "2022-02-02",
                    "2023-01-01",
                ],
            }
        )

        filter_not_collectable(input_data, "not_collectable")

        input_data.reset_index(drop=True, inplace=True)

        expected_output = pd.DataFrame(
            {
                "id": ["2", "3", "4"],
                "status": ["late", "not_collectable", "paid"],
                "history_date": ["2022-01-02", "2022-02-02", "2023-01-01"],
            }
        )

        expected_output["history_date"] = pd.to_datetime(
            expected_output["history_date"], format="mixed", dayfirst=True
        ).dt.date
        assert_frame_equal(input_data, expected_output)

    def test_drop_rows_by_status(self):
        input_data = pd.DataFrame(
            {"id": ["1", "2", "3", "4"], "status": ["active", "late", "active", "paid"]}
        )
        drop_rows_by_status(input_data, "active")

        input_data.reset_index(drop=True, inplace=True)

        expected_output = pd.DataFrame({"id": ["2", "4"], "status": ["late", "paid"]})

        assert_frame_equal(input_data, expected_output)

    def test_drop_rows_by_current_status_dates(self):
        input_data = pd.DataFrame(
            {
                "id": ["1", "1", "2", "2", "3", "3"],
                "status": [
                    "late",
                    "elapsed",
                    "paid",
                    "paid",
                    "elapsed",
                    "paid_distributor",
                ],
                "history_date": [
                    "2022-01-01",
                    "2022-02-01",
                    "2022-01-01",
                    "2022-02-01",
                    "2022-01-01",
                    "2022-02-01",
                ],
            }
        )

        drop_rows_by_current_status_dates(input_data, "elapsed")
        input_data.reset_index(drop=True, inplace=True)

        expected_output = pd.DataFrame(
            {
                "id": ["2", "2", "3", "3"],
                "status": ["paid", "paid", "elapsed", "paid_distributor"],
                "history_date": [
                    "2022-01-01",
                    "2022-02-01",
                    "2022-01-01",
                    "2022-02-01",
                ],
            }
        )

        assert_frame_equal(input_data, expected_output)

    def test_drop_policy_rows_if_ever_status(self):
        input_data = pd.DataFrame(
            {
                "id": ["1", "1", "2", "3", "3", "4"],
                "status": [
                    "pay_installments",
                    "cancelled",
                    "recovery_underway",
                    "claim_rejected",
                    "cancelled",
                    "paid",
                ],
            }
        )

        drop_policy_rows_if_ever_status(input_data, "cancelled")
        input_data.reset_index(drop=True, inplace=True)

        # Expected output
        expected_output = pd.DataFrame(
            {"id": ["2", "4"], "status": ["recovery_underway", "paid"]}
        )

        assert_frame_equal(input_data, expected_output)
