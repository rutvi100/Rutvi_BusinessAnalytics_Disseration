import pandas as pd
import os
import sys
from pathlib import Path

from hoodsio.tuin.models import CompanyTUIN

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())

from src.utils.constants import CONFIG_DIR
import src.utils.load_params

loader = src.utils.load_params
params = loader.load_params(CONFIG_DIR / "global" / "dvc_params.yaml")


def drop_current_appointment_from_other_appointments(
    officer_appointments, other_appointments_column
):
    """
    This function makes sure that we exclude any current appointment and removes duplicates
    :param officer_appointments: The final dataframe from the get_bad_officer_other_appointments stage which includes the bad officers, their company and other appointments
    :param other_appointments_column: The column in the dataframe that contains the other appointments
    :return: A final dataframe excluding any current appointments and duplicates
    """
    # TODO: remove drop_duplicates this once duplicate tuin officers are handled
    officer_appointments.drop_duplicates(inplace=True)

    for index, row in officer_appointments.iterrows():
        company_numbers = row[other_appointments_column].split(" ")
        current_co_tuin_id = row["current_appointment"]

        for company_number in company_numbers:
            try:
                company_tuin = CompanyTUIN.objects.get(
                    company_number=company_number, company_country="GB"
                )
            except CompanyTUIN.DoesNotExist as e:
                print(f"Company {company_number} not found")
                raise e
            co = str(company_tuin.id)

            if current_co_tuin_id == co:
                company_numbers.remove(company_number)
        officer_appointments.at[index, other_appointments_column] = " ".join(
            company_numbers
        )

    num_officers_without_other_appointment = (
        officer_appointments[other_appointments_column].isnull().sum()
    )
    logger.warning(
        f"{num_officers_without_other_appointment} officers don't have a other appointment"
    )

    return officer_appointments


if __name__ == "__main__":
    from src.utils.constants import LOG_NAME, LOG_LEVEL, LOG_DIR
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    officer_data = pd.read_csv(params["OFFICER_OTHER_APPOINTMENTS"])

    drop_current_appointment_from_other_appointments(
        officer_data, "other_appointments_company_reg_number"
    ).to_csv(params["OFFICER_CURRENT_OTHER_APPOINTMENTS"], index=False)
