import os
import sys
from pathlib import Path
import argparse

import pandas as pd

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())

import src.utils.load_params
from src.utils.constants import CONFIG_DIR

loader = src.utils.load_params
params = loader.load_params(CONFIG_DIR / "global" / "dvc_params.yaml")


class OfficerIdArgParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(description="Agr parser for data preparation")
        self.add_argument(
            "--label_type",
            metavar="label_type",
            default="bad",
            help="label value ; see GOOD_LABEL and BAD_LABEL in dvc_params.yaml",
        )


def get_other_officer_appointments(officer_appointments, bad_officers):
    """
    Seeing if there is any overlap between pnp appointment files and officers we labelled bad
    :param officer_appointments : pnp appointment files
    :param bad_officers : bad officers
    :return: gives us the common officers between the two input files
    """

    other_officer_appointments = pd.merge(
        officer_appointments,
        bad_officers,
        how="inner",
        left_on="officer_id",
        right_on="officer_number",
    )[["company_id", "officer_number", "company_ids"]]

    other_officer_appointments.columns = [
        "current_appointment",
        "officer_number",
        "other_appointments_company_reg_number",
    ]

    return pd.DataFrame(
        other_officer_appointments,
    )


if __name__ == "__main__":
    from src.utils.constants import CONFIG_DIR, LOG_DIR, LOG_LEVEL, LOG_NAME
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    args = OfficerIdArgParser().parse_args()
    label_type = args.label_type

    officer_appointments = pd.read_csv(params["OFFICER_APPOINTMENTS"])

    officers_of_label_type = pd.read_csv(
        params[f"{label_type.upper()}_COMPANY_OFFICER_NUMBER"]
    )

    other_officer_appointments_extracted = get_other_officer_appointments(
        officer_appointments, officers_of_label_type
    )

    other_officer_appointments_extracted.to_csv(
        params[f"{label_type.upper()}_OFFICER_OTHER_APPOINTMENTS"], index=False
    )

    # Log the count of officers not mapped to officer_appointments
    unmapped_officers_count = len(officers_of_label_type) - len(
        other_officer_appointments_extracted
    )
    logger.info(
        f"Number of {label_type.upper()} officers not mapped to officer_appointments: {unmapped_officers_count}"
    )
