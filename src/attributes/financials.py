def measure_financials(officer_attributes, other_appointment_dict):
    officer_attributes["financials"] = {}

    other_reg_numbers = list(other_appointment_dict.keys())

    other_financial_info = {
        "other": {
            other_reg_number: [
                {
                    "trade_debtors": company_financial.get("trade_debtors").get(
                        "value", 0
                    ),
                    "total_assets": company_financial.get("total_assets").get(
                        "value", 0
                    ),
                    "trade_creditors": company_financial.get("trade_creditors").get(
                        "value", 0
                    ),
                    "current_assets": company_financial.get("current_assets").get(
                        "value", 0
                    ),
                    "current_liabilities": company_financial.get(
                        "current_liabilities"
                    ).get("value", 0),
                    "turnover": company_financial.get("turnover").get("value", 0),
                    "ebitda": company_financial.get("ebitda").get("value", 0),
                    "publication_date": company_financial.get("publication_date", None),
                    "accounts_date": company_financial.get("accounts_date", None),
                    "accountant": company_financial.get("accountant").get(
                        "sourceName", None
                    ),
                    "solicitor": company_financial.get("solicitor").get(
                        "sourceName", None
                    ),
                    "jointAuditor": company_financial.get("jointAuditor").get(
                        "sourceName", None
                    ),
                    "auditor": company_financial.get("auditor").get("sourceName", None),
                }
                for company_financial in other_appointment_dict[other_reg_number].get(
                    "company_financials", []
                )
            ]
            for other_reg_number in other_reg_numbers
        }
    }

    officer_attributes["financials"].update(other_financial_info)
