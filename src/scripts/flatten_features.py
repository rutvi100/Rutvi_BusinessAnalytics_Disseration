import pandas as pd
import json
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)

from pathlib import Path

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())

import src.utils.load_params
from src.utils.constants import CONFIG_DIR

loader = src.utils.load_params
params = loader.load_params(CONFIG_DIR / "global" / "dvc_params.yaml")

def flatten_json_data(data, prefix=''):
    flattened_data = {}
    for key, value in data.items():
        if isinstance(value, dict):
            nested_data = flatten_json_data(value, prefix + key + '_')
            flattened_data.update(nested_data)
        else:
            if prefix:
                flattened_data[prefix.split('_')[0] + '_' + key] = value
            else:
                flattened_data[key] = value
    return flattened_data


def fill_nan_with_zero(df):
    '''

    :param df: the flattened dataframe
    :return: returns all the NaN values as 0 for the filing columns
    '''
    df_copy = df.copy()
    mask = df_copy.columns.str.startswith('filings')
    # Use the mask to select the relevant columns and fill NaN values with 0
    df_copy.loc[:, mask] = df_copy.loc[:, mask].fillna(0.0)
    return df_copy

if __name__ == "__main__":
    from src.utils.constants import CONFIG_DIR, LOG_DIR, LOG_LEVEL, LOG_NAME
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    flattened_data_dict = {}

    directory = params['OFFICER_FEATURES_DIRECTORY']

    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename)) as file:
            data = json.load(file)
            officer_number = filename.split('.')[0]
            flattened_data = flatten_json_data(data)
            flattened_data_dict[officer_number] = flattened_data

    flattened_data = pd.DataFrame.from_dict(flattened_data_dict, orient='index')
    flattened_data.insert(0, 'officer_number', flattened_data.index)

    #flattened_data_converted = fill_nan_with_zero(flattened_data)

    officer_appointments = pd.read_csv(params['OFFICER_OTHER_APPOINTMENTS'])

    flattened_features_appointments = pd.merge(flattened_data, officer_appointments[['officer_number', 'label', 'current_appointment']],
                           on='officer_number', how='left')

    officers_with_multiple_labels = flattened_features_appointments.groupby('officer_number')['label'].nunique()
    officers_with_multiple_labels = officers_with_multiple_labels[officers_with_multiple_labels > 1].index
    flattened_features_appointments.loc[flattened_features_appointments['officer_number'].isin(officers_with_multiple_labels), 'label'] = 1

    earliest_observation_dates = pd.read_csv(params['EARLIEST_CO_OBSERVATION'])

    flattened_features_appointment_policy = pd.merge(flattened_features_appointments, earliest_observation_dates[['policy', 'observation_date', 'company']],
                               left_on='current_appointment', right_on='company', how='left')

    flattened_features_appointment_policy['observation_date'] = pd.to_datetime(flattened_features_appointment_policy['observation_date'])

    flattened_features_appointment_policy.sort_values('observation_date', inplace=True)

    officer_flattened_dataset = flattened_features_appointment_policy.drop_duplicates(subset=['officer_number', 'label'], keep='first')

    officer_flattened_dataset.to_csv(params["OFFICER_FEATURE_DATASET"], index=False)