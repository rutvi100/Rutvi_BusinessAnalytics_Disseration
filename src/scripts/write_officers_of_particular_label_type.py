import argparse
import os
import sys
from pathlib import Path

import pandas as pd
from hoodsio.tuin.models import CompanyOfficerAppointment, CompanyTUIN

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


def get_officer_number(companies_of_label_type):
    """
    This function gets the officer number and role for our bad companies.
    We can then see the overlap between the bad officers here and the ones in the pnp appointment files
    :param companies_of_label_type: takes in the bad company ids for which we want to extract the officer role and number
    :return: returns the officer number and role for the bad companies
    """
    appointments = CompanyOfficerAppointment.objects.filter(
        company__in=companies_of_label_type.current_appointment
    )

    officers = [(str(i.company.id), i.officer.officer_number) for i in appointments]
    officers_df = pd.DataFrame(officers)
    officers_df.columns = ["company_id", "officer_number"]

    return officers_df


def drop_duplicate_tuin_officers(
    officers_with_duplicates, old_to_new_duedil_mapping, logger
):
    """
    At some point, duedil changed their officer numbers.
    As we always save the officer appointment in tuin after calling the duedil endpoint, we have ended up with duplicate officers.
    In this function, we take the old and new numbers and:
    - if there is a new number assigned to the old number, and both are present, we drop the old number
    - if there is not a new number assigned to the old number, we don't drop the old number

    - - - CASE STUDY - - -

    Tuin company id : co-encaWxUvTKVSKLbHia2JNB
    Officer : Allistair John KENT

    officer number : affe255848586269b5d9664cd372b115476e72f2 created `2022-03-18`
    officer  number : 21da1452b625c3c6b28cbaa7a96d1c0d4f05878e created `2020-11-09`

    In old_to_new_duedil_mapping affe255848586269b5d9664cd372b115476e72f2 is found in the new_officer_number column.
    We wish to only keep the initial entry,


     - - - - - - - - - - -
    :param officers: list of officer appointments
    :param old_to_new_duedil_mapping: mapping of old officer number to new officer number

    """

    drop_count = 0
    assert_failed = 0

    for tuin_company_id in officers_with_duplicates.company_id.unique():
        # Here we are fetching what the new officer numbers used to be.
        # We dropna as we aren't concerned with mappings to NaN
        old_officer_numbers_to_drop = (
            old_to_new_duedil_mapping[
                old_to_new_duedil_mapping.new_officer_number.isin(
                    officers_with_duplicates[
                        officers_with_duplicates.company_id == tuin_company_id
                    ].officer_number.values
                )
            ]
            .drop_duplicates()
            .dropna()
        )

        # We aren't concerned with the mappings where old and new numbers are the same
        old_officer_numbers_to_drop = old_officer_numbers_to_drop[
            old_officer_numbers_to_drop.old_officer_number
            != old_officer_numbers_to_drop.new_officer_number
        ]

        officers = CompanyOfficerAppointment.objects.filter(company=tuin_company_id)
        for to_drop, to_keep in old_officer_numbers_to_drop[
            ["old_officer_number", "new_officer_number"]
        ].values:
            logger.info(f"drop {to_drop}, keep {to_keep}")
            if not officers.filter(officer__officer_number=to_drop).exists():
                continue

            drop_count += 1

            logger.info(
                f"Found duplicate officers in company {tuin_company_id}({CompanyTUIN.objects.get(id=tuin_company_id).company_number})"
            )
            to_drop_appt = (
                officers.filter(officer__officer_number=to_drop).first().officer
            )
            to_keep_appt = (
                officers.filter(officer__officer_number=to_keep).first().officer
            )

            try:
                assert to_drop_appt.created < to_keep_appt.created
            except:
                assert_failed += 1
                logger.info(
                    "Dropped officer has more recent created date, probably not a problem (see issue 6) failed for following ..."
                )

            logger.info(
                f"Dropping officer {to_drop}:\nf {to_drop_appt.officer_first_name} {to_drop_appt.officer_last_name} (created {to_drop_appt.created.date()}) (role {officers.filter(officer__officer_number=to_drop).first().role.role_description})"
            )
            logger.info(
                f"Keeping officer {to_keep}:\nf {to_keep_appt.officer_first_name} {to_keep_appt.officer_last_name} (created {to_keep_appt.created.date()}) (role {officers.filter(officer__officer_number=to_keep).first().role.role_description})"
            )
            officers_with_duplicates = officers_with_duplicates[
                ~(
                    (officers_with_duplicates.company_id == tuin_company_id)
                    & (officers_with_duplicates["officer_number"] == to_drop)
                )
            ]

    logger.info(f"Dropped {drop_count} officers !")
    logger.info(f"Assert failed {assert_failed} times !")
    return officers_with_duplicates


if __name__ == "__main__":
    from src.utils.constants import CONFIG_DIR, LOG_DIR, LOG_LEVEL, LOG_NAME
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    args = OfficerIdArgParser().parse_args()
    label_type = args.label_type

    companies_of_label_type = pd.read_csv(
        params[f"UNIQUE_LIST_{label_type.upper()}_COMPANIES"]
    )

    # Get list of officers from tuin - as tuin has dirty data whereby some officers are
    # duplicated they will need to be cleaned to remove these duplicated officers
    officers_with_duplicates = get_officer_number(companies_of_label_type)

    old_to_new_duedil_mapping = pd.read_csv(params["DUEDIL_OLD_NEW_OFFICER_NUMBERS"])

    drop_duplicates_logger = get_logger(
        "drop_duplicate_tuin_officers", LOG_LEVEL, LOG_DIR
    )
    drop_duplicates_logger.info(
        f"Dropping duplicate officers for {label_type.upper()} companies...\n"
    )
    officers_without_duplicates = drop_duplicate_tuin_officers(
        officers_with_duplicates, old_to_new_duedil_mapping, drop_duplicates_logger
    )

    officers_without_duplicates.to_csv(
        params[f"{label_type.upper()}_COMPANY_OFFICER_NUMBER"], index=False
    )
