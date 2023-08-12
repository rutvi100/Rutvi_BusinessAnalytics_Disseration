import unittest
import sys
import pandas as pd
import os
from pandas.testing import assert_frame_equal


sys.path.append(os.getcwd())

from src.scripts.write_officer_appointments import extract_officer_and_company_ids


class TestWriteAllCompanies(unittest.TestCase):
    def test_extract_officer_and_company_ids(self):
        folder_path = "tests/test_appointment_files/"
        files_ = os.listdir(folder_path)

        input_result = extract_officer_and_company_ids(
            files_, "tests/test_appointment_files/"
        )

        expected_output = pd.DataFrame(
            {"officer_id": ["100", "200"], "company_ids": ["1111", "2345,6789,0156"]}
        )

        assert_frame_equal(input_result, expected_output)
