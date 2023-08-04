from src.utils.constants import LOG_NAME, LOG_LEVEL, LOG_DIR, CONFIG_DIR
from src.utils.custom_logging import get_logger

attribute_building_bugs_logger = get_logger(
    "attribute_building_bugs", LOG_LEVEL, LOG_DIR
)


def measure_sector(
    officer_attributes,
    current_appointment_dict,
    other_appointment_dict,
    attribute_building_bugs_logger,
):
    officer_attributes["sector"] = {}

    current_reg_number = next(iter(current_appointment_dict.keys()))
    other_reg_numbers = list(other_appointment_dict.keys())

    current_sector_info = {"current": {}}

    try:
        current_sector_info["current"][current_reg_number] = {
            "sector_code": current_appointment_dict[current_reg_number]
            .get("sector_info")
            .get("sector_code"),
            "sector_description": current_appointment_dict[current_reg_number]
            .get("sector_info")
            .get("sector_description"),
            "sector_group_description": current_appointment_dict[current_reg_number]
            .get("sector_info")
            .get("sector_group_description"),
        }
    except AttributeError as e:
        # Log the exception and relevant information using the custom logger
        attribute_building_bugs_logger.error(
            f"Error building sector attributes for current_reg_number: {current_reg_number}"
        )
        attribute_building_bugs_logger.error(str(e))
        current_sector_info["current"][current_reg_number] = {
            "sector_code": "unknown",
            "sector_description": "unknown",
            "sector_group_description": "unknown",
        }

    officer_attributes["sector"].update(current_sector_info)

    other_sector_info = {"other": {}}

    for other_reg_number in other_reg_numbers:
        try:
            other_sector_info["other"][other_reg_number] = {
                "sector_code": other_appointment_dict[other_reg_number]
                .get("sector_info")
                .get("sector_code"),
                "sector_description": other_appointment_dict[other_reg_number]
                .get("sector_info")
                .get("sector_description"),
                "sector_group_description": other_appointment_dict[other_reg_number]
                .get("sector_info")
                .get("sector_group_description"),
            }
        except AttributeError as e:
            # Log the exception and relevant information using the custom logger
            attribute_building_bugs_logger.error(
                f"Error building sector attributes for reg_number: {other_reg_number}"
            )
            attribute_building_bugs_logger.error(str(e))
            other_sector_info["other"][current_reg_number] = {
                "sector_code": "unknown",
                "sector_description": "unknown",
                "sector_group_description": "unknown",
            }

    officer_attributes["sector"].update(other_sector_info)
