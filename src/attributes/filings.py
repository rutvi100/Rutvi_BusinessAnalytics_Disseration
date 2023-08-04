from src.utils.constants import LOG_NAME, LOG_LEVEL, LOG_DIR, CONFIG_DIR
from src.utils.custom_logging import get_logger

attribute_building_bugs_logger = get_logger(
    "attribute_building_bugs", LOG_LEVEL, LOG_DIR
)


def measure_filings(officer_attributes, other_appointment_dict):
    officer_attributes["filings"] = {}

    other_reg_numbers = list(other_appointment_dict.keys())

    other_filing_info = {"other": {}}

    for other_reg_number in other_reg_numbers:
        company_filings = other_appointment_dict[other_reg_number].get(
            "company_filings"
        )
        if company_filings is not None and company_filings['filings'] is not None:
            filing_list = []
            for company_filing in company_filings["filings"]:
                filing_data = {
                    "date": company_filing.get("date", "unknown"),
                    "type": company_filing.get("type", "unknown"),
                    "category": company_filing.get("category", "unknown"),
                    "action_date": company_filing.get("action_date", "unknown"),
                    "description": company_filing.get("description", "unknown"),
                    "subcategory": company_filing.get("subcategory", "unknown"),
                    "description_values": company_filing.get(
                        "description_values", "unknown"
                    ),
                }
                filing_list.append(filing_data)
            other_filing_info["other"][other_reg_number] = filing_list

    officer_attributes["filings"].update(other_filing_info)
