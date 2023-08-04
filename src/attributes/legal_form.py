from src.utils.constants import LOG_NAME, LOG_LEVEL, LOG_DIR, CONFIG_DIR
from src.utils.custom_logging import get_logger

attribute_building_bugs_logger = get_logger(
    "attribute_building_bugs", LOG_LEVEL, LOG_DIR
)


def measure_legal_form(
    officer_attributes,
    current_appointment_dict,
    other_appointment_dict,
    attribute_building_bugs_logger,
):
    officer_attributes["legal_form"] = {}

    current_reg_number = next(iter(current_appointment_dict.keys()))
    other_reg_numbers = list(other_appointment_dict.keys())

    current_legal_info = {"current": {}}
    try:
        current_legal_info["current"][current_reg_number] = {
            "legal_form_code": next(
                iter(current_appointment_dict[current_reg_number].get("legal_form"))
            ).get("legal_form_code"),
            "legal_form_description": next(
                iter(current_appointment_dict[current_reg_number].get("legal_form"))
            ).get("legal_form_description"),
        }
    except Exception as e:
        attribute_building_bugs_logger.error(
            f"Error building legal form attributes for current_reg_number: {current_reg_number}"
        )
        attribute_building_bugs_logger.error(str(e))
        current_legal_info["current"][current_reg_number] = {
            "legal_form_code": "unknown",
            "legal_form_description": "unknown",
        }

    officer_attributes["legal_form"].update(current_legal_info)

    other_legal_info = {"other": {}}
    for other_reg_number in other_reg_numbers:
        try:
            other_legal_info["other"][other_reg_number] = {
                "legal_form_code": next(
                    iter(other_appointment_dict[other_reg_number].get("legal_form"))
                ).get("legal_form_code"),
                "legal_form_description": next(
                    iter(other_appointment_dict[other_reg_number].get("legal_form"))
                ).get("legal_form_description"),
            }
        # TODO should be specific to AttributeError, TypeError, StopIteration
        except Exception as e:
            # Log the exception and relevant information using the custom logger
            attribute_building_bugs_logger.error(
                f"Error building sector attributes for reg_number: {other_reg_number}"
            )
            attribute_building_bugs_logger.error(str(e))
            other_legal_info["other"][other_reg_number] = {
                "legal_form_code": "unknown",
                "legal_form_description": "unknown",
            }

    officer_attributes["legal_form"].update(other_legal_info)
