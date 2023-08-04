import statistics
from datetime import datetime, timedelta
def extract_officer_appointment_data(officer_data):
    '''
    :param officer_data: officer data containing all attributes
    :return: data specific to officer appointments
    '''
    officer_appointment_data = []

    officer = officer_data.get('officer', {})
    birthday = officer.get('birthday')

    other_appointments = officer.get('other', {})

    for company_number, appointments_list in other_appointments.items():
        for appointment in appointments_list:
            appointment_start_date = appointment['appointment_start_date']
            appointment_end_date = appointment['appointment_end_date']
            officer_role = appointment['officer_role']
            officer_appointment_data.append({'company_number': company_number, 'appointment_start_date': appointment_start_date, 'appointment_end_date': appointment_end_date, 'officer_role': officer_role, 'birthday': birthday})

    return officer_appointment_data

def get_total_appointment_counts(officer_appointment_data, observation_date):
    '''
    :param officer_appointment_data: the data that includes officer appointment information
    :param observation_date: the observation date. we only want to count those appointments whose appointment end date is greater than or equal to the specified observation date
    :return: the output consists of a dictionary which consists of each duration and its count
    '''
    observation_datetime = datetime.strptime(observation_date, '%Y-%m-%d')
    counts = {}

    durations = [0, 3, 6, 12, 24, 36, 'all']

    for duration in durations:
        if duration == 'all':
            last_x_months_date = datetime.strptime('1900-01-01', '%Y-%m-%d')
        else:
            last_x_months_date = observation_datetime - timedelta(days=duration * 30)

        filtered_data = [
            appointment for appointment in officer_appointment_data if
            appointment['appointment_end_date'] == 'unknown' or
            datetime.strptime(appointment['appointment_end_date'], '%Y-%m-%d') >= last_x_months_date
        ]

        count = len(filtered_data)
        key = f"total_number_of_appointments_{duration}_months"
        counts[key] = count

    return {'total_number_of_appointments': counts}

def get_total_appointment_role_counts(officer_appointment_data, observation_date):
    '''
    :param officer_appointment_data: the data that includes officer appointment information
    :param observation_date: the observation date. we only want to count those appointments whose appointment end date is greater than or equal to the specified observation date
    :return: the output consists of a dictionary which consists of each role and its count for different durations
    '''
    observation_datetime = datetime.strptime(observation_date, '%Y-%m-%d')
    counts = {}

    durations = [0, 3, 6, 12, 24, 36, 'all']

    for duration in durations:
        if duration == 'all':
            last_x_months_date = datetime.strptime('1900-01-01', '%Y-%m-%d')
        else:
            last_x_months_date = observation_datetime - timedelta(days=duration * 30)

        filtered_data = [
            appointment for appointment in officer_appointment_data if
            appointment['appointment_end_date'] == 'unknown' or
            datetime.strptime(appointment['appointment_end_date'], '%Y-%m-%d') >= last_x_months_date
        ]

        role_counts = {}
        for appointment in filtered_data:
            role = appointment['officer_role']
            role_key = f"{role}_count_{duration}_months"
            role_counts[role_key] = role_counts.get(role_key, 0) + 1

        counts.update(role_counts)

    return {'total_number_of_officer_role_appointments': counts}

def get_officer_nationality(officer_data):
    '''
    :param officer_data: officer attribute data for the input officer
    :return: returns the officer's nationality
    '''
    officer_nationality = next(iter(officer_data.get('nationality', {})), None)

    return officer_nationality

def calculate_officer_age(data, aggregation):
    '''
    :param data: the data that includes officer appointment information
    :param aggregation:  the aggregation type - mean, median, min or max
    :return: returns the officer age for the officer in question
    '''
    company_ages = {}

    appointments_by_company = {}
    for entry in data:
        company_number = entry['company_number']
        if company_number not in appointments_by_company:
            appointments_by_company[company_number] = []
        appointments_by_company[company_number].append(entry)

    for company_number, appointments in appointments_by_company.items():
        latest_start_date = min(appointments, key=lambda x: datetime.strptime(x['appointment_start_date'], '%Y-%m-%d'))['appointment_start_date']
        birthday = appointments[0]['birthday']

        if birthday == 'unknown':
            officer_age = 'unknown'
        else:
            birthday = datetime.strptime(birthday, '%Y-%m-%d')
            officer_age = datetime.strptime(latest_start_date, '%Y-%m-%d') - birthday
            officer_age = officer_age.days / 365

        company_ages[company_number] = officer_age

    valid_ages = [age for age in company_ages.values() if age != 'unknown' and age >= 10]

    if aggregation == 'mean':
        result = round(statistics.mean(valid_ages), 2) if valid_ages else 'unknown'
    elif aggregation == 'median':
        result = round(statistics.median(valid_ages), 2) if valid_ages else 'unknown'
    elif aggregation == 'min':
        result = round(min(valid_ages), 2) if valid_ages else 'unknown'
    elif aggregation == 'max':
        result = round(max(valid_ages), 2) if valid_ages else 'unknown'
    else:
        raise ValueError("Invalid aggregation. Choose from 'mean', 'median', 'min', or 'max'.")

    return {f'{aggregation}_officer_age_at_appointment': result}
