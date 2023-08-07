import os
from tqdm import tqdm
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
import json
from hoodsio.tuin.models import CompanyTUIN

from pathlib import Path
import sys

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())

from src.utils.constants import CONFIG_DIR
import src.utils.load_params

loader = src.utils.load_params
params = loader.load_params(CONFIG_DIR / "global" / "dvc_params.yaml")

from src.utils.extract_other_appointment_information import (
    get_company_address,
    get_company_sector,
    get_company_legal_form,
    get_company_financials,
    get_company_parent_child,
    get_company_officer_appointments,
    get_company_filings,
    get_officers_nationality,
)


def update_other_appointment_info(
    company_number, other_appointments_company_info_directory, logger
):
    """
    :param company_number: The other appointment company number
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
        data["company_filings"] = get_company_filings(company_tuin, logger)
        data["legal_form"] = get_company_legal_form(company_tuin)
        data["company_officer_appointment"] = get_company_officer_appointments(
            company_tuin
        )
        data["company_financials"] = get_company_financials(company_tuin)
        data["company_parent_child"] = get_company_parent_child(company_tuin)
        data["all_officers_nationalities"] = get_officers_nationality(company_tuin)

        with open(file_path, "w") as f:
            json.dump(data, f)

    except Exception as e:
        e = str(e)
        logger.warning(f"Unexpected Error for {company_number} : {e}")

        with open(file_path, "w") as f:
            json.dump({"error": "ObjectDoesNotExist", "message": e}, f)


if __name__ == "__main__":
    from src.utils.constants import LOG_NAME, LOG_LEVEL, LOG_DIR
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    appointments_df = pd.read_csv(params["OFFICER_CURRENT_OTHER_APPOINTMENTS"])
    other_appointment_company_numbers = set(
        appointments_df["other_appointments_company_reg_number"]
        .str.split()
        .dropna()
        .explode()
        .values
    )

    other_appointments_company_info_directory = params[
        "OTHER_APPOINTMENT_COMPANY_INFO_DIRECTORY"
    ]

    os.makedirs(other_appointments_company_info_directory, exist_ok=True)

    for other_appointment_company_number in tqdm(
        list(set(other_appointment_company_numbers)),
        total=len(set(other_appointment_company_numbers)),
    ):
        update_other_appointment_info(
            other_appointment_company_number,
            other_appointments_company_info_directory,
            logger,
        )
