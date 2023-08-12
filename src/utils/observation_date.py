import pandas as pd
from datetime import datetime

def get_observation_date(officer_appointments, earliest_observation_dates, officer_number):
    '''
    :param officer_number: officer number of the officer in question
    :return: returns the observation date for the officer based on the current appointment and policy
    '''
    merged_df = pd.merge(officer_appointments, earliest_observation_dates, left_on='current_appointment', right_on='company')
    observation_date = merged_df.loc[merged_df['officer_number'] == officer_number, 'observation_date'].values[0]
    return observation_date

def filter_data_on_observation_date(attribute_data, date_column, observation_date):
    '''
    :param attribute_data: Data containing the officer attribute information
    :param date_column: The date column that we want to compare the observation date with
    :param observation_date: the observation date of the policy
    :return: returns only those rows where the date column is lesser than the observation date
    '''
    observation_date = datetime.strptime(observation_date, '%Y-%m-%d')

    filtered_data = []
    for data in attribute_data:
        if data[date_column]:
            date_col = datetime.strptime(data[date_column], '%Y-%m-%d')
            if date_col < observation_date:
                filtered_data.append(data)

    return filtered_data
