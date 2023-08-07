import pandas as pd
import os
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

def get_cut_off_date(officer_data):
    bad_officers_sorted = officer_data[officer_feature_data['label'] == 1].sort_values('observation_date', ascending=False)
    cutoff_index = int(len(bad_officers_sorted) * 0.1)
    return bad_officers_sorted.iloc[cutoff_index]['observation_date']

if __name__ == "__main__":
    from src.utils.constants import CONFIG_DIR, LOG_DIR, LOG_LEVEL, LOG_NAME
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    officer_feature_data = pd.read_csv(params['OFFICER_FEATURE_DATASET'])

    officer_feature_data = officer_feature_data.dropna(subset=['label'])

    cut_off_date = get_cut_off_date(officer_feature_data)

    officer_feature_data_sorted = officer_feature_data.sort_values('observation_date', ascending=False)

    backtesting_data = officer_feature_data_sorted[officer_feature_data_sorted['observation_date'] > cut_off_date]
    modelling_data = officer_feature_data_sorted[officer_feature_data_sorted['observation_date'] <= cut_off_date]

    modelling_data.to_csv(params['MODELLING_DATASET'], index=False)
    backtesting_data.to_csv(params['BACKTESTING_DATASET'], index=False)