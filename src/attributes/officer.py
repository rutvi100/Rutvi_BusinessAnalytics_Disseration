import calendar
import json
from collections import Counter
from datetime import date, datetime

import pandas as pd
from hoodsio.tuin.models import Officer, OfficerNationality


def calculate_birthday(appointment):
    officer_birth_year = appointment.get("officer_birthyear")
    officer_birth_month = appointment.get("officer_birthmonth")
    if not officer_birth_year or not officer_birth_month:
        return "unknown"

    _, last_day = calendar.monthrange(officer_birth_year, officer_birth_month)
    officer_date_of_birth = str(
        datetime(officer_birth_year, officer_birth_month, last_day).date()
    )
    return officer_date_of_birth


def calculate_appointment_length(appointment):
    appointment_start_date = appointment["officer_appointment_start_date"]
    appointment_end_date = appointment["officer_appointment_end_date"]
    start_date = datetime.strptime(appointment_start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(appointment_end_date, "%Y-%m-%d").date()

    appointment_length = (end_date - start_date).days / 365.25
    appointment_length = round(appointment_length, 2)
    if appointment_length < 0:
        return str(start_date), "unknown", "unknown"
    elif appointment_length > 100:
        return str(start_date), "unknown", "unknown"
    else:
        return str(start_date), str(end_date), str(appointment_length)


def company_has_officer_appointments(other_appointment_data):
    return "company_officer_appointment" in other_appointment_data


def measure_officer_nationality(
    officer_attributes,
    officer_number,
):
    # TODO need to understand why there are multiple Officer objects, taking first for now
    officer_attributes["nationality"] = dict(
        Counter(
            [
                i.officer_nationality_code
                for i in OfficerNationality.objects.filter(
                    officer=Officer.objects.filter(officer_number=officer_number)[0]
                )
            ]
        )
    )

def measure_appointment_attributes(
    officer_attributes,
    officer_number,
    other_appointments_dict,
    current_appointments_dict,
    attribute_building_bugs_logger,
):
    officer = officer_attributes.setdefault("officer", {})

    appointments_dict = {
        "current": current_appointments_dict,
        "other": other_appointments_dict,
    }

    birthdays = []

    for appointment_type in appointments_dict:

        officer_attributes["officer"].setdefault(appointment_type, {})

        for company_reg_number, other_appointment_data in appointments_dict[
            appointment_type
        ].items():

            officer_attributes["officer"][appointment_type].setdefault(
                company_reg_number, []
            )

            if not company_has_officer_appointments(other_appointment_data):
                continue

            appointments = other_appointment_data["company_officer_appointment"]

            for appointment in appointments:
                if appointment["officer_number"] != officer_number:
                    continue

                (
                    appointment_start_date,
                    appointment_end_date,
                    appointment_length,
                ) = calculate_appointment_length(appointment)

                officer_role = appointment["officer_role"]

                officer_first_name = appointment["officer_first_name"]
                officer_middle_name = appointment["officer_middle_name"]
                officer_last_name = appointment["officer_last_name"]
                officer_is_shareholder = (
                    1 if appointment["officer_is_shareholder"] else 0
                )
                officer_is_company = appointment.get("officer_is_company")
                officer_type = appointment.get("officer_type")

                officer_attributes["officer"][appointment_type][
                    company_reg_number
                ].append(
                    {
                        "appointment_start_date": appointment_start_date,
                        "appointment_end_date": appointment_end_date,
                        "appointment_length": appointment_length,
                        "officer_role": officer_role,
                        "officer_first_name": officer_first_name,
                        "officer_middle_name": officer_middle_name,
                        "officer_last_name": officer_last_name,
                        "officer_is_shareholder": officer_is_shareholder,
                        "officer_is_company": officer_is_company,
                        "officer_type": officer_type,
                    }
                )
                # This will either return unknown if one of birth_month or birth_year aren't
                # known, else it will return a string of the birth year
                birthday = calculate_birthday(appointment)

                if birthday != "unknown":
                    birthdays.append(birthday)

    if len(set(birthdays)) > 1:
        birthday = max(Counter(birthdays))
        attribute_building_bugs_logger.info(
            f"Several birthdays found for officer {officer_number} ({Counter(birthdays)}), taking most common (birthday)"
        )
    elif len(set(birthdays)) == 1:
        birthday = birthdays[0]
    else:
        birthday = "unknown"

    officer_attributes["officer"]["birthday"] = birthday
