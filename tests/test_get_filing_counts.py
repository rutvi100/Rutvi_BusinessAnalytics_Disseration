import unittest
import sys
import os

sys.path.append(os.getcwd())

from src.features.filings import get_filing_counts

class TestFilingCounts(unittest.TestCase):

    def test_get_filing_counts(self):
        observation_date = '2023-01-01'

        input_list = [{'type': 'SH01', 'date': '2023-04-03'},
                        {'type': 'SH01', 'date': '2022-12-16'},
                        {'type': 'SH01', 'date': '2022-12-16'},
                        {'type': 'SH01', 'date': '2021-10-22'},
                        {'type': 'SH01', 'date': '2019-12-20'},
                        {'type': 'SH01', 'date': '2018-09-18'}]

        actual_output = get_filing_counts(input_list, observation_date)

        expected_output = {'filings': {'SH01': {'sum_appt_SH01_3_months': 0,
                                                'sum_appt_SH01_6_months': 0,
                                                'sum_appt_SH01_12_months': 2,
                                                'sum_appt_SH01_24_months': 3,
                                                'sum_appt_SH01_36_months': 3,
                                                'sum_appt_SH01_all_months': 5}}}

        self.assertEqual(actual_output, expected_output)

    def test_get_filing_counts_multiple_filing_types(self):
        observation_date = '2023-01-01'

        input_list = [{'type': 'SH01', 'date': '2023-04-03'},
                      {'type': 'SH01', 'date': '2022-12-16'},
                      {'type': 'SH01', 'date': '2022-12-16'},
                      {'type': 'SH01', 'date': '2021-10-22'},
                      {'type': 'TM01', 'date': '2020-05-29'},
                      {'type': 'SH01', 'date': '2019-12-20'},
                      {'type': 'SH01', 'date': '2018-09-18'},
                      {'type': 'TM01', 'date': '2017-07-18'},
                      {'type': 'TM01', 'date': '2016-06-27'},
                      {'type': 'TM01', 'date': '2015-06-18'},
                      {'type': 'TM01', 'date': '2015-02-17'},
                      {'type': 'TM01', 'date': '2014-09-04'},
                      {'type': 'TM01', 'date': '2012-04-05'},
                      {'type': 'TM01', 'date': '2012-04-05'},
                      {'type': 'TM01', 'date': '2012-04-04'},
                      {'type': 'TM01', 'date': '2012-04-04'},
                      {'type': 'TM01', 'date': '2012-04-04'},
                      {'type': 'TM01', 'date': '2011-07-14'},
                      {'type': 'TM01', 'date': '2010-10-12'},
                      {'type': 'TM01', 'date': '2010-01-19'},
                      {'type': 'TM01', 'date': '2010-01-04'}]

        actual_output = get_filing_counts(input_list, observation_date)

        expected_output = {'filings': {'SH01': {'sum_appt_SH01_3_months': 0,
                                                'sum_appt_SH01_6_months': 0,
                                                'sum_appt_SH01_12_months': 2,
                                                'sum_appt_SH01_24_months': 3,
                                                'sum_appt_SH01_36_months': 3,
                                                'sum_appt_SH01_all_months': 5},
                                       'TM01': {'sum_appt_TM01_3_months': 0,
                                                'sum_appt_TM01_6_months': 0,
                                                'sum_appt_TM01_12_months': 0,
                                                'sum_appt_TM01_24_months': 0,
                                                'sum_appt_TM01_36_months': 0,
                                                'sum_appt_TM01_all_months': 15}}}

        self.assertEqual(actual_output, expected_output)