from datetime import datetime

from src.utils.formatters import serialize_datetime
from django.core.exceptions import ObjectDoesNotExist

import sys
import os
import sys
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from hoodsio.tuin.models import (
    CompanyAddress,
    Officer,
    OfficerNationality,
    CompanyFilings,
    CompanyFinancials,
    CompanyLegalForm,
    CompanyOfficerAppointment,
    CompanyParentChild,
    CompanySector,
    CompanySize,
    CompanyTUIN,
)
from src.utils.formatters import serialize_datetime

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())


import src.utils.load_params
from src.utils.constants import CONFIG_DIR

loader = src.utils.load_params
params = loader.load_params(CONFIG_DIR / "global" / "dvc_params.yaml")


def get_company_address(company_tuin):
    """
    :param company_tuin: Other appointment company tuin id
    :return: Returns the company address information for the company_tuin parameter
    """
    company_addresses = CompanyAddress.objects.filter(company=company_tuin)

    address_data = [
        {
            "full_address": company_address.full_address,
            "postcode": company_address.postcode,
            "county": company_address.county,
            "country": company_address.country,
            "latitude": float(company_address.latitude),
            "longitude": float(company_address.longitude),
            "address_type": company_address.address_type.address_type_description,
        }
        for company_address in company_addresses
    ]

    return address_data


def get_company_sector(company_tuin, logger):
    """
    :param company_tuin: Other appointment company tuin id
    :return: Returns the company sector information for the company_tuin parameter
    """
    try:
        company_sector = CompanySector.objects.get(company=company_tuin, order=1)
    except ObjectDoesNotExist as e:
        logger.warning(
            f"Failed to extract sector information for company {company_tuin.company_number}:\n{e}"
        )
        sector_data = {
            "sector_type": None,
            "sector_description": None,
            "sector_group_description": None,
            "sector_code": None,
        }
        return sector_data

    sector_data = {
        "sector_type": company_sector.sector.sector_type,
        "sector_description": company_sector.sector.sector_description,
        "sector_group_description": company_sector.sector.sector_group_description,
        "sector_code": company_sector.sector.sector_code,
    }

    return sector_data


def get_company_filings(company_tuin, logger):
    """
    :param company_tuin: Other appointment company tuin id
    :return: Returns the company filing information for the company_tuin parameter
    """
    try:
        company_filing = CompanyFilings.objects.get(company=company_tuin)
    except ObjectDoesNotExist as e:
        logger.warning(
            f"Failed to extract filing information for company {company_tuin.company_number}:\n{e}"
        )
        filing_data = {
            "filings": None,
            "filing_origin": None,
            "filing_created": None,
            "filing_modified": None,
        }
        return filing_data
    filing_data = {
        "filings": company_filing.filings,
        "filing_origin": company_filing.origin,
        "filing_created": serialize_datetime(company_filing.created),
        "filing_modified": serialize_datetime(company_filing.modified),
    }

    return filing_data


def get_company_financials(company_tuin):
    """
    :param company_tuin: Other appointment company tuin id
    :return: Returns the company financial information for the company_tuin parameter
    """
    company_financials = CompanyFinancials.objects.filter(company=company_tuin)

    # Sort the financials according to date in descending order
    company_financials = sorted(
        company_financials,
        key=lambda x: x.company_financials_accounts_date,
        reverse=True,
    )

    financial_data = []
    for company_financial in company_financials:
        total_assets = company_financial.company_financials_metrics.get("totalAssets")

        if total_assets and total_assets.get("value") and total_assets.get("value") > 1:
            financial_data.append(
                {
                    "accounts_date": serialize_datetime(
                        company_financial.company_financials_accounts_date
                    ),
                    "total_assets": total_assets,
                    "trade_debtors": company_financial.company_financials_metrics.get(
                        "tradeDebtors"
                    ),
                    "trade_creditors": company_financial.company_financials_metrics.get(
                        "tradeCreditors"
                    ),
                    "current_assets": company_financial.company_financials_metrics.get(
                        "currentAssets"
                    ),
                    "current_liabilities": company_financial.company_financials_metrics.get(
                        "currentLiabilities"
                    ),
                    "accountant": company_financial.company_financials_metrics.get(
                        "accountant"
                    ),
                    "auditor": company_financial.company_financials_metrics.get(
                        "auditor"
                    ),
                    "solicitor": company_financial.company_financials_metrics.get(
                        "solicitor"
                    ),
                    "jointAuditor": company_financial.company_financials_metrics.get(
                        "jointAuditor"
                    ),
                    "turnover": company_financial.company_financials_metrics.get(
                        "turnover"
                    ),
                    "ebitda": company_financial.company_financials_metrics.get(
                        "ebitda"
                    ),
                    "reporting_period": company_financial.company_financials_reporting_period,
                    "consolidated_accounts": company_financial.company_financials_consolidated_accounts,
                    "currency": company_financial.company_financials_currency,
                    "publication_date": serialize_datetime(
                        company_financial.company_financials_publication_date
                    ),
                    "created": serialize_datetime(company_financial.created),
                    "modified": serialize_datetime(company_financial.modified),
                }
            )

    return financial_data


def get_company_legal_form(company_tuin):
    """
    :param company_tuin: Other appointment company tuin id
    :return: Returns the company legal information for the company_tuin parameter
    """
    company_legal_forms = CompanyLegalForm.objects.filter(company=company_tuin)

    legal_data = [
        {
            "legal_form_code": company_legal_form.legal_form.legal_form_code,
            "legal_form_description": company_legal_form.legal_form.legal_form_description,
        }
        for company_legal_form in company_legal_forms
    ]

    return legal_data


def get_company_officer_appointments(company_tuin):
    """
    :param company_tuin: Other appointment company tuin id
    :return: Returns the company officer appointment information for the company_tuin parameter
    """
    company_officer_appointments = CompanyOfficerAppointment.objects.filter(
        company=company_tuin
    )

    officer_appointment_data = [
        {
            "officer_appointment_start_date": serialize_datetime(
                appointment.appointment_start_date
            ),
            "officer_appointment_end_date": serialize_datetime(
                appointment.appointment_end_date
            ),
            "officer_first_name": appointment.officer.officer_first_name,
            "officer_middle_name": appointment.officer.officer_middle_name,
            "officer_last_name": appointment.officer.officer_last_name,
            "officer_is_shareholder": appointment.officer.officer_is_shareholder,
            "officer_birthyear": appointment.officer.officer_birthyear,
            "officer_birthmonth": appointment.officer.officer_birthmonth,
            "officer_type": appointment.officer.officer_type,
            "officer_is_company": appointment.officer.is_company,
            "officer_number": appointment.officer.officer_number,
            "officer_number_source": appointment.officer.officer_number_source,
            "officer_created": serialize_datetime(appointment.officer.created),
            "officer_modified": serialize_datetime(appointment.officer.modified),
            "officer_role": appointment.role.role_description,
            "officer_role_created": serialize_datetime(appointment.role.created),
            "officer_role_modified": serialize_datetime(appointment.role.modified),
        }
        for appointment in company_officer_appointments
    ]

    return officer_appointment_data


def get_officer_nationality(officer_number):
    nationalities = OfficerNationality.objects.filter(
        officer=Officer.objects.get(officer_number=officer_number)
    )


def get_officers_nationality(company_tuin):
    company_officer_appointments = CompanyOfficerAppointment.objects.filter(
        company=company_tuin
    )

    officer_appointment_nationality = [
        {
            "officer_number": appointment.officer.officer_number,
            "officer_nationality_code": [
                i.officer_nationality_code
                for i in OfficerNationality.objects.filter(officer=appointment.officer)
            ]
            if OfficerNationality.objects.filter(officer=appointment.officer).exists()
            else None,
        }
        for appointment in company_officer_appointments
    ]

    return officer_appointment_nationality


def get_company_parent_child(company_tuin):
    """
    :param company_tuin: Other appointment company tuin id
    :return: Returns the company parent child information for the company_tuin parameter
    """

    parent_companies = CompanyParentChild.objects.filter(parent=company_tuin)
    child_companies = CompanyParentChild.objects.filter(child=company_tuin)
    parent_child_data = []

    for parent in parent_companies:
        parent_child_data.append(
            {
                "parent_company_child": str(parent.child.id),
                "parent_company_parent": str(parent.parent.id),
                "parent_company_degree_of_separation": parent.degree_of_separation,
                "parent_company_immediate_parent": parent.is_immediate_parent,
                "parent_company_ultimate_parent": parent.is_ultimate_parent,
            }
        )

    for child in child_companies:
        parent_child_data.append(
            {
                "child_company_child": str(child.child.id),
                "child_company_parent": str(child.parent.id),
                "child_company_degree_of_separation": child.degree_of_separation,
                "child_company_immediate_parent": child.is_immediate_parent,
                "child_company_ultimate_parent": child.is_ultimate_parent,
            }
        )

    return parent_child_data


if __name__ == "__main__":
    from src.utils.constants import LOG_DIR, LOG_LEVEL, LOG_NAME
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")
