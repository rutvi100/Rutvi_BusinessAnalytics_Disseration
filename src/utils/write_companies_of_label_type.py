import pandas as pd
import sys
import csv
import os
import argparse

from pathlib import Path

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())

from src.utils.constants import CONFIG_DIR
import src.utils.load_params

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


def get_labelled_companies(labelled_gb_policies, label, label_column="label"):
    """
    This function is a generic function that returns the list of bad companies
    :param labelled_gb_policies: The labelled_gb_policies you input containing the debtor id, labeland other fields
    :param label_column: The label column name in your labelled_gb_policiesset
    :return: returns a unique list of companies labelled 1 (bad company)
    """
    return (
        labelled_gb_policies[labelled_gb_policies[label_column] == label]["debtor_id"]
        .unique()
        .tolist()
    )


if __name__ == "__main__":
    from src.utils.constants import LOG_NAME, LOG_LEVEL, LOG_DIR, CONFIG_DIR
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    args = OfficerIdArgParser().parse_args()
    label_type = args.label_type
    label = int(params[f"{label_type.upper()}_LABEL"])

    labelled_gb_policies = pd.read_csv(params["LABELED_GB_POLICIES"])

    company_list = get_labelled_companies(labelled_gb_policies, label)

    company_df = pd.DataFrame(company_list)
    company_df.columns = ["current_appointment"]
    company_df.to_csv(
        params[f"UNIQUE_LIST_{label_type.upper()}_COMPANIES"], index=False
    )
