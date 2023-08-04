import pandas as pd

def measure_address(
    officer_attributes,
    current_appointment_dict,
    other_appointment_dict,
    officer_service_address,
):
    officer_attributes["address"] = {}

    current_reg_number = next(iter(current_appointment_dict.keys()))
    other_reg_numbers = list(other_appointment_dict.keys())

    current_address_info = {
        "current": {
            current_reg_number: [
                {
                    "full_address": company_address.get("full_address"),
                    "latitude": company_address.get("latitude"),
                    "longitude": company_address.get("longitude"),
                    "address_type": company_address.get("address_type"),
                    "postcode": company_address.get("postcode"),
                    "county": company_address.get("county"),
                    "country": company_address.get("country"),
                }
                for company_address in current_appointment_dict[current_reg_number].get(
                    "address_info", []
                )
            ]
        }
    }
    officer_attributes["address"].update(current_address_info)

    other_address_info = {
        "other": {
            other_reg_number: [
                {
                    "full_address": company_address.get("full_address"),
                    "latitude": company_address.get("latitude"),
                    "longitude": company_address.get("longitude"),
                    "address_type": company_address.get("address_type"),
                    "postcode": company_address.get("postcode"),
                    "county": company_address.get("county"),
                    "country": company_address.get("country"),
                }
                for company_address in other_appointment_dict[other_reg_number].get(
                    "address_info", []
                )
            ]
            for other_reg_number in other_reg_numbers
        }
    }

    officer_attributes["address"].update(other_address_info)

    if not officer_service_address.empty:
        if isinstance(officer_service_address, pd.Series):
            officer_service_address = pd.DataFrame(officer_service_address).T

        service_address_info = {}
        for index, row in officer_service_address.iterrows():
            service_address_number = row["company_id"]

            service_address_info["service:"] = {
                str(service_address_number): {
                    "service_full_address": row["full_address"],
                    "service_premises": row["premises"],
                    "service_post_town": row["post_town"],
                    "service_county": row["county"],
                    "service_postcode": row["postcode"],
                    "service_country_code": row["country_code"],
                }
            }

        officer_attributes["address"]["service"] = {
            service_address_number: service_address_info
        }
