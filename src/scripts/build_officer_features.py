import os
import json
import pandas as pd
from tqdm import tqdm
import logging
import sys

logging.basicConfig(level=logging.INFO)

from pathlib import Path

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())

import src.utils.load_params
from src.utils.constants import CONFIG_DIR

loader = src.utils.load_params
params = loader.load_params(CONFIG_DIR / "global" / "dvc_params.yaml")

from src.utils.observation_date import get_observation_date, filter_data_on_observation_date
from src.features.filings import extract_filing_data_company, get_sum_filing_counts, get_aggregated_filing_counts
from src.features.sector import compare_current_other_sector
from src.features.officer_appointments import extract_officer_appointment_data, get_total_appointment_counts, get_total_appointment_role_counts, get_officer_nationality, calculate_officer_age
from src.features.financials import extract_financial_data, calculate_time_to_publish_accounts, calculate_metric_to_total_assets, check_financial_company_flag
def open_officer_file(officer_number):
    '''
    :param officer_number: file names which are the officer number
    :return: returns all the data inside the file
    '''
    file_path = os.path.join(officer_directory, f"{officer_number}.json")
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def process_officer_features(officer_number):
    '''
    :param officer_number: the officer number which is the file name
    :return: returns the features in the officer_features dictionary for the input officer number
    '''
    officer_data = open_officer_file(officer_number)
    observation_date = get_observation_date(officer_appointments, earliest_observation_dates, officer_number)

    officer_features = {}

    #Filings features
    filing_data = extract_filing_data_company(officer_data)
    filtered_filings_data = filter_data_on_observation_date(filing_data, 'date', observation_date)
    filing_counts = get_sum_filing_counts(filtered_filings_data, observation_date)
    avg_filing_counts = get_aggregated_filing_counts(filtered_filings_data, observation_date, aggregation='mean')
    filing_counts.update(avg_filing_counts)
    median_filing_counts = get_aggregated_filing_counts(filtered_filings_data, observation_date, aggregation='median')
    filing_counts.update(median_filing_counts)
    min_filing_counts = get_aggregated_filing_counts(filtered_filings_data, observation_date, aggregation='min')
    filing_counts.update(min_filing_counts)
    max_filing_counts = get_aggregated_filing_counts(filtered_filings_data, observation_date, aggregation='max')
    filing_counts.update(max_filing_counts)
    officer_features['filings'] = filing_counts
    #Sector features
    officer_features['sector'] = compare_current_other_sector(officer_data)
    #Officer attribute features
    appointment_data = extract_officer_appointment_data(officer_data)
    filtered_officer_appointment_data = filter_data_on_observation_date(appointment_data, 'appointment_start_date', observation_date)
    appointment_counts = get_total_appointment_counts(filtered_officer_appointment_data, observation_date)
    officer_role_appointment_counts = get_total_appointment_role_counts(filtered_officer_appointment_data, observation_date)
    appointment_counts.update(officer_role_appointment_counts)
    mean_officer_age = calculate_officer_age(filtered_officer_appointment_data, aggregation= 'mean')
    appointment_counts.update(mean_officer_age)
    median_officer_age = calculate_officer_age(filtered_officer_appointment_data, aggregation= 'median')
    appointment_counts.update(median_officer_age)
    min_officer_age = calculate_officer_age(filtered_officer_appointment_data, aggregation= 'min')
    appointment_counts.update(min_officer_age)
    max_officer_age = calculate_officer_age(filtered_officer_appointment_data, aggregation= 'max')
    appointment_counts.update(max_officer_age)
    officer_features['officer'] = appointment_counts
    officer_features['nationality'] = get_officer_nationality(officer_data)
    #Financials features
    financial_data = extract_financial_data(officer_data)
    filtered_financial_data = filter_data_on_observation_date(financial_data, 'publication_date', observation_date)
    mean_time_to_publish_financials = calculate_time_to_publish_accounts(filtered_financial_data, aggregation= 'mean')
    median_time_to_publish_financials = calculate_time_to_publish_accounts(filtered_financial_data, aggregation= 'median')
    mean_time_to_publish_financials.update(median_time_to_publish_financials)
    min_time_to_publish_financials = calculate_time_to_publish_accounts(filtered_financial_data, aggregation= 'min')
    mean_time_to_publish_financials.update(min_time_to_publish_financials)
    max_time_to_publish_financials = calculate_time_to_publish_accounts(filtered_financial_data, aggregation= 'max')
    mean_time_to_publish_financials.update(max_time_to_publish_financials)
    mean_current_assets_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'current_assets', aggregation='mean')
    mean_time_to_publish_financials.update(mean_current_assets_to_total_assets)
    mean_current_liabilities_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'current_liabilities', aggregation='mean')
    mean_time_to_publish_financials.update(mean_current_liabilities_to_total_assets)
    mean_trade_creditors_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'trade_creditors', aggregation='mean')
    mean_time_to_publish_financials.update(mean_trade_creditors_to_total_assets)
    mean_trade_debtors_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'trade_debtors', aggregation='mean')
    mean_time_to_publish_financials.update(mean_trade_debtors_to_total_assets)
    mean_turnover_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'turnover', aggregation='mean')
    mean_time_to_publish_financials.update(mean_turnover_to_total_assets)
    mean_ebitda_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'ebitda', aggregation='mean')
    mean_time_to_publish_financials.update(mean_ebitda_to_total_assets)
    median_current_assets_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'current_assets', aggregation='median')
    mean_time_to_publish_financials.update(median_current_assets_to_total_assets)
    median_current_liabilities_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'current_liabilities', aggregation='median')
    mean_time_to_publish_financials.update(median_current_liabilities_to_total_assets)
    median_trade_creditors_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'trade_creditors', aggregation='median')
    mean_time_to_publish_financials.update(median_trade_creditors_to_total_assets)
    median_trade_debtors_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'trade_debtors', aggregation='median')
    mean_time_to_publish_financials.update(median_trade_debtors_to_total_assets)
    median_turnover_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'turnover', aggregation='median')
    mean_time_to_publish_financials.update(median_turnover_to_total_assets)
    median_ebitda_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'ebitda', aggregation='median')
    mean_time_to_publish_financials.update(median_ebitda_to_total_assets)
    min_current_assets_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'current_assets', aggregation='min')
    mean_time_to_publish_financials.update(min_current_assets_to_total_assets)
    min_current_liabilities_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'current_liabilities', aggregation='min')
    mean_time_to_publish_financials.update(min_current_liabilities_to_total_assets)
    min_trade_creditors_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'trade_creditors', aggregation='min')
    mean_time_to_publish_financials.update(min_trade_creditors_to_total_assets)
    min_trade_debtors_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'trade_debtors', aggregation='min')
    mean_time_to_publish_financials.update(min_trade_debtors_to_total_assets)
    min_turnover_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'turnover', aggregation='min')
    mean_time_to_publish_financials.update(min_turnover_to_total_assets)
    min_ebitda_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'ebitda', aggregation='min')
    mean_time_to_publish_financials.update(min_ebitda_to_total_assets)
    max_current_assets_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'current_assets', aggregation='max')
    mean_time_to_publish_financials.update(max_current_assets_to_total_assets)
    max_current_liabilities_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'current_liabilities', aggregation='max')
    mean_time_to_publish_financials.update(max_current_liabilities_to_total_assets)
    max_trade_creditors_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'trade_creditors', aggregation='max')
    mean_time_to_publish_financials.update(max_trade_creditors_to_total_assets)
    max_trade_debtors_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'trade_debtors', aggregation='max')
    mean_time_to_publish_financials.update(max_trade_debtors_to_total_assets)
    max_turnover_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'turnover', aggregation='max')
    mean_time_to_publish_financials.update(max_turnover_to_total_assets)
    max_ebitda_to_total_assets = calculate_metric_to_total_assets(filtered_financial_data, 'ebitda', aggregation='max')
    mean_time_to_publish_financials.update(max_ebitda_to_total_assets)
    financial_company_flag = check_financial_company_flag(financial_data, observation_date)
    mean_time_to_publish_financials.update(financial_company_flag)
    officer_features['financials'] = mean_time_to_publish_financials
    return officer_features

def save_officer_features(officer_number, officer_features):
    '''
    :param officer_number: input officer number file
    :param officer_features: features here includes the previous function's output of all the features of the officer based on sector, officer, filings and financials.
    :return: Opens the respective officer file and dumps the data in that
    '''
    feature_directory = os.path.join('data', 'officer_feature_store')
    feature_file = os.path.join(feature_directory, f"{officer_number}.json")
    os.makedirs(feature_directory, exist_ok=True)
    with open(feature_file, "w") as f:
        json.dump(officer_features, f)

if __name__ == "__main__":
    from src.utils.constants import CONFIG_DIR, LOG_DIR, LOG_LEVEL, LOG_NAME
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    officer_directory = params['OFFICER_ATTRIBUTES_DIRECTORY']
    feature_directory = params['OFFICER_FEATURES_DIRECTORY']

    earliest_observation_dates = pd.read_csv(params['EARLIEST_CO_OBSERVATION'])
    officer_appointments = pd.read_csv(params['OFFICER_OTHER_APPOINTMENTS'])

    officer_files = os.listdir(officer_directory)

    progress_bar = tqdm(total=len(officer_files))
    for officer_file in officer_files:
        officer_number = os.path.splitext(officer_file)[0]
        officer_features = process_officer_features(officer_number)
        save_officer_features(officer_number, officer_features)
        progress_bar.update(1)

    progress_bar.close()