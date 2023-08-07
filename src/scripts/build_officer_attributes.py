import json
import os
import sys
from pathlib import Path

import pandas as pd
from hoodsio.tuin.models import CompanyTUIN
from tqdm import tqdm

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())
import src.utils.load_params
from src.attributes.address import measure_address
from src.attributes.filings import measure_filings
from src.attributes.financials import measure_financials
from src.attributes.legal_form import measure_legal_form
from src.attributes.officer import (
    measure_appointment_attributes,
    measure_officer_nationality,
)
from src.attributes.parent_child import measure_company_parent_child
from src.attributes.sector import measure_sector
from src.utils.constants import CONFIG_DIR
from src.utils.exceptions import CustomException, CustomFileNotFoundError

loader = src.utils.load_params
params = loader.load_params(CONFIG_DIR / "global" / "dvc_params.yaml")


def get_other_appointments(other_appointments, logger):
    other_appointment_dict = {}
    for other_appointment in other_appointments.split():
        file_path = (
            params["OTHER_APPOINTMENT_COMPANY_INFO_DIRECTORY"] + other_appointment
        )

        try:
            with open(file_path, "r") as f:
                other_appointment_data = json.load(f)
            other_appointment_dict[other_appointment] = other_appointment_data

        except FileNotFoundError:
            logger.error(
                f"File not found for officer {officer_number}. File: {file_path} and other appointment {other_appointment}"
            )
            continue

    return other_appointment_dict


def get_current_appointment(current_appointment, logger):
    try:
        company_number = CompanyTUIN.objects.get(id=current_appointment).company_number
    except CompanyTUIN.DoesNotExist:
        raise CustomException(current_appointment)

    file_path = (
        f"{params['CURRENT_APPOINTMENT_COMPANY_INFO_DIRECTORY']}{company_number}"
    )
    current_appointment_data = {}

    try:
        with open(file_path, "r") as f:
            current_appointment_data = json.load(f)

    except FileNotFoundError:
        logger.error(f"File not found for officer {officer_number}. File: {file_path}")
        pass

    current_appointment_dict = {company_number: current_appointment_data}
    return current_appointment_dict


def write_officer_with_no_other_appointments(officer_number):
    no_other_appointments_dir = params["NO_OTHER_APPOINTMENTS_DIRECTORY"]
    os.makedirs(no_other_appointments_dir, exist_ok=True)
    no_other_appointments_file = f"{no_other_appointments_dir}/{officer_number}.json"
    with open(no_other_appointments_file, "w") as f:
        json.dump({}, f)


if __name__ == "__main__":
    from src.utils.constants import CONFIG_DIR, LOG_DIR, LOG_LEVEL, LOG_NAME
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    attribute_building_bugs_logger = get_logger(
        "attribute_building_bugs", LOG_LEVEL, LOG_DIR
    )

    officer_other_appointments = pd.read_csv(
        params["OFFICER_CURRENT_OTHER_APPOINTMENTS"]
    )

    officer_service_addresses = pd.read_csv(
        params["OFFICER_SERVICE_ADDRESS_APPOINTMENTS"]
    )
    officer_service_addresses.set_index("officer_id", inplace=True)

    attributes_dir = params["OFFICER_ATTRIBUTES_DIRECTORY"]
    os.makedirs(attributes_dir, exist_ok=True)

    # TODO why are there duplicates in this?
    for _, row in tqdm(
        officer_other_appointments.iterrows(),
        total=len(officer_other_appointments),
    ):

        officer_attributes = {}

        current_appointment, officer_number, other_appointments = (
            row.current_appointment,
            row.officer_number,
            row.other_appointments_company_reg_number,
        )

        if str(other_appointments) == "nan":
            write_officer_with_no_other_appointments(officer_number)
            continue

        if not all(
            [
                os.path.exists(
                    f"data/officer_other_appointment_company_information/{i}"
                )
                for i in other_appointments.split()
            ]
        ):
            # TODO log that there is some appointment information missing for {company number}, which company info is missing
            continue

        if not os.path.exists(
            f"data/officer_current_appointment_company_information/{CompanyTUIN.objects.get(id=current_appointment).company_number}"
        ):
            # TODO Same logging, ecept make known it's current
            continue

        other_appointments_dict = get_other_appointments(other_appointments, logger)

        current_appointment_dict = get_current_appointment(current_appointment, logger)

        # TODO it could be useful to look at the nationalities of the other officers at the company
        # that information can be found in all_officer
        measure_officer_nationality(officer_attributes, officer_number)
        measure_appointment_attributes(
            officer_attributes,
            officer_number,
            other_appointments_dict,
            current_appointment_dict,
            attribute_building_bugs_logger,
        )
        measure_sector(
            officer_attributes,
            current_appointment_dict,
            other_appointments_dict,
            attribute_building_bugs_logger,
        )
        measure_legal_form(
            officer_attributes,
            current_appointment_dict,
            other_appointments_dict,
            attribute_building_bugs_logger,
        )
        # TODO why are so many officers without a service address
        try:
            officer_service_address = officer_service_addresses.loc[officer_number]
        except KeyError:
            officer_service_address = pd.DataFrame()
        measure_address(
            officer_attributes,
            current_appointment_dict,
            other_appointments_dict,
            officer_service_address,
        )
        measure_filings(officer_attributes, other_appointments_dict)
        measure_financials(officer_attributes, other_appointments_dict)
        measure_company_parent_child(officer_attributes, other_appointments_dict)

        with open(f"{attributes_dir}/{officer_number}.json", "w") as f:
            json.dump(officer_attributes, f)

    logger.info(
        f"Total number of companies in data/officer_attribute_store: {len(officer_attributes)}"
    )
