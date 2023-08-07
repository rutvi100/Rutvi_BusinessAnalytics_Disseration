import os
import json
import pandas as pd
import sys

from pathlib import Path

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())

from src.utils.constants import CONFIG_DIR
import src.utils.load_params

loader = src.utils.load_params
params = loader.load_params(CONFIG_DIR / "global" / "dvc_params.yaml")

# The duplicates in the DataFrame could be due to multiple appointments for the same officer
# and company having the same service address.
# In the provided example data, it appears that the officer with
# officer_id "2f509d171b7aed8d101fd60181b20e9f02303d57" has two
# appointments with the same company and service address, resulting in duplicate rows.
# without removing duplicates, we get 243077 rows.
# after removing duplicates, we get 219370 rows.


def extract_service_addresses(officer_appointment_files, officer_appointment_file_path):
    """
    Extracts the service addresses for each officer and company from the officer appointment files.

    :param officer_appointment_files: List of officer appointment files.
    :param officer_appointment_file_path: Path to the directory containing the officer appointment files.
    :return: DataFrame containing officer ID, company ID, and service address details.
    """
    service_addresses = []

    for file_name in officer_appointment_files:
        file_path = os.path.join(officer_appointment_file_path, file_name)
        with open(file_path, "r") as f:
            file_data = json.load(f)

        officer_id = file_data["officerId"]

        for company in file_data["companies"]:
            company_id = company["companyId"]

            for appointment in company["appointments"]:
                address_info = appointment.get("serviceAddress")
                if address_info is not None and "fullAddress" in address_info:
                    full_address = address_info["fullAddress"]
                    structured_address = address_info.get("structuredAddress")
                    premises = (
                        structured_address.get("premises")
                        if structured_address
                        else None
                    )
                    post_town = (
                        structured_address.get("postTown")
                        if structured_address
                        else None
                    )
                    county = (
                        structured_address.get("county") if structured_address else None
                    )
                    postcode = (
                        structured_address.get("postcode")
                        if structured_address
                        else None
                    )
                    country_code = (
                        structured_address.get("countryCode")
                        if structured_address
                        else None
                    )

                    service_address_details = {
                        "officer_id": officer_id,
                        "company_id": company_id,
                        "full_address": full_address,
                        "premises": premises,
                        "post_town": post_town,
                        "county": county,
                        "postcode": postcode,
                        "country_code": country_code,
                    }
                    service_addresses.append(service_address_details)

    service_addresses_df = pd.DataFrame(service_addresses)
    service_addresses_df = service_addresses_df.drop_duplicates()
    return service_addresses_df


if __name__ == "__main__":
    from src.utils.constants import LOG_NAME, LOG_LEVEL, LOG_DIR, CONFIG_DIR
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    # Loading the pnp officer appointment files
    officer_appointment_file_path = params["OFFICER_APPOINTMENTS_FILES"]

    officer_appointment_files = os.listdir(officer_appointment_file_path)

    all_service_addresses = extract_service_addresses(
        officer_appointment_files, officer_appointment_file_path
    )

    all_service_addresses.to_csv(
        params["OFFICER_SERVICE_ADDRESS_APPOINTMENTS"], index=False
    )

all_service_addresses = extract_service_addresses(
    officer_appointment_files, officer_appointment_file_path
)
