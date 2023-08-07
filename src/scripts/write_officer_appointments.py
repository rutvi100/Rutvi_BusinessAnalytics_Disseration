import os
import argparse
import json
import sys
import pandas as pd


from pathlib import Path

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())

from src.utils.constants import CONFIG_DIR
import src.utils.load_params

loader = src.utils.load_params
params = loader.load_params(CONFIG_DIR / "global" / "dvc_params.yaml")


def extract_officer_and_company_ids(
    officer_appointment_files, officer_appointment_file_path
):
    """
    :param officer_appointment_files: all the officer_appointment_files present in that file path
    :param officer_appointment_file_path: the file path
    :return: returns the companies that each officer is associated with
    """
    officer_appointments_list = []

    for file_name in officer_appointment_files:
        file_officer_appointments_list = json.load(
            open(f"{officer_appointment_file_path}{file_name}")
        )
        officer_id = file_officer_appointments_list["officerId"]
        company_ids = [
            company["companyId"]
            for company in file_officer_appointments_list["companies"]
        ]

        officer_appointments_list.append(
            {"officer_id": officer_id, "company_ids": " ".join(company_ids)}
        )

    return pd.DataFrame(officer_appointments_list)


if __name__ == "__main__":
    from src.utils.constants import LOG_NAME, LOG_LEVEL, LOG_DIR, CONFIG_DIR
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    # Loading the pnp officer appointment files
    officer_appointment_file_path = params["OFFICER_APPOINTMENTS_FILES"]

    officer_appointment_files = os.listdir(officer_appointment_file_path)

    officer_appointments = extract_officer_and_company_ids(
        officer_appointment_files, officer_appointment_file_path
    )

    officer_appointments.to_csv(params["OFFICER_APPOINTMENTS"], index=False)
