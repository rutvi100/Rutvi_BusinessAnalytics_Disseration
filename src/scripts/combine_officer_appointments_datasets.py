import pandas as pd
import os
import sys

from pathlib import Path

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())

from src.utils.constants import CONFIG_DIR
import src.utils.load_params

loader = src.utils.load_params
params = loader.load_params(CONFIG_DIR / "global" / "dvc_params.yaml")


def combine_other_appointments(good_officer_appointments, bad_officer_appointments):
    """
    :param good_officer_appointments: all the other appointments of the good officers
    :param bad_officer_appointments: all the other appointments of the bad officers
    :return: the combine dataframe of the other appointments of both, the good and bad officers
    """
    return pd.concat([good_officer_appointments, bad_officer_appointments], axis=0)


if __name__ == "__main__":
    from src.utils.constants import LOG_NAME, LOG_LEVEL, LOG_DIR, CONFIG_DIR
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    bad_officer_other_appointments = pd.read_csv(
        params["BAD_OFFICER_OTHER_APPOINTMENTS"]
    )
    bad_officer_other_appointments["label"] = 1
    good_officer_other_appointments = pd.read_csv(
        params["GOOD_OFFICER_OTHER_APPOINTMENTS"]
    )
    good_officer_other_appointments["label"] = 0
    # TODO: need to decide how we will handle officers that are labelled good and bad

    # TODO: remove drop_duplciates this once duplicate tuin officers are handled
    combine_other_appointments(
        bad_officer_other_appointments, good_officer_other_appointments
    ).drop_duplicates().to_csv(params["OFFICER_OTHER_APPOINTMENTS"], index=False)
