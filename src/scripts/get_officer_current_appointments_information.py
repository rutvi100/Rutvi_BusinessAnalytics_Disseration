import json
import os
import sys
from pathlib import Path

import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from hoodsio.tuin.models import CompanyTUIN
from tqdm import tqdm

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())

import src.utils.load_params
from src.utils.constants import CONFIG_DIR

loader = src.utils.load_params
params = loader.load_params(CONFIG_DIR / "global" / "dvc_params.yaml")

from src.utils.extract_other_appointment_information import (
    get_company_address,
    get_company_legal_form,
    get_company_officer_appointments,
    get_company_sector,
    get_officers_nationality,
)


def update_current_appointment_info(
    company_number, other_appointments_company_info_directory, logger
):
    """
    :param company_number: The current appointment company number
    :param other_appointments_company_info_directory: The directory that we want to put all the other appointment data in
    :return: Returns a directory was all the other appointment information for all the other appointments
    """
    file_path = f"{other_appointments_company_info_directory}{company_number}"
    try:
        company_tuin = CompanyTUIN.objects.get(
            company_number=company_number, company_country="GB"
        )

    except ObjectDoesNotExist:
        print(f"CompanyTUIN object not found for company number: {company_number}")
        logger.warning(
            f"CompanyTUIN object not found for company number: {company_number}"
        )

        with open(file_path, "w") as f:
            json.dump({"error": "CompanyTUIN object is not found"}, f)

    try:
        data = {}

        data["tuin_company_id"] = str(company_tuin.id)
        data["address_info"] = get_company_address(company_tuin)
        data["sector_info"] = get_company_sector(company_tuin, logger)
        data["company_officer_appointment"] = get_company_officer_appointments(
            company_tuin
        )
        data["legal_form"] = get_company_legal_form(company_tuin)
        data["all_officers_nationalities"] = get_officers_nationality(company_tuin)

        with open(file_path, "w") as f:
            json.dump(data, f)

    except Exception as e:
        e = str(e)
        logger.warning(f"Unexpected Error for {company_number} : {e}")

        with open(file_path, "w") as f:
            json.dump({"error": "ObjectDoesNotExist", "message": e}, f)


if __name__ == "__main__":
    from src.utils.constants import LOG_DIR, LOG_LEVEL, LOG_NAME
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    appointments_df = pd.read_csv(params["OFFICER_CURRENT_OTHER_APPOINTMENTS"])

    current_appointment_tuin_ids = set(appointments_df["current_appointment"])

    company_numbers = [
        CompanyTUIN.objects.get(id=current_appointment_tuin_id).company_number
        for current_appointment_tuin_id in current_appointment_tuin_ids
        if CompanyTUIN.objects.filter(id=current_appointment_tuin_id).exists()
    ]

    present_appointments_company_info_directory = params[
        "CURRENT_APPOINTMENT_COMPANY_INFO_DIRECTORY"
    ]

    os.makedirs(present_appointments_company_info_directory, exist_ok=True)

    for company_number in tqdm(
        list(set(company_numbers)), total=len(set(company_numbers))
    ):
        update_current_appointment_info(
            company_number, present_appointments_company_info_directory, logger
        )
