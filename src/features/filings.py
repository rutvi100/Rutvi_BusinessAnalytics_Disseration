import statistics
from datetime import datetime, timedelta
def extract_filing_data_company(officer_data):
    '''
    :param officer_data: officer data containing all attributes
    :return: data specific to filings
    '''
    filing_data = []

    other_filings = officer_data.get('filings', {}).get('other', {})

    for company_number, filings_list in other_filings.items():
        for filing in filings_list:
            filing_type = filing['type']
            filing_date = filing['date']
            filing_data.append({'company_number': company_number, 'type': filing_type, 'date': filing_date})

    return filing_data

def get_sum_filing_counts(filing_data, observation_date):
    '''
    :param filing_data: the data that includes only the filing type and date
    :param observation_date: the observation date. we only want to count those filings whose filing date is lesser than the observation date
    :return: the output consists of a dictionary which consists of each filing type and its count
    '''
    observation_datetime = datetime.strptime(observation_date, '%Y-%m-%d')
    counts = {}

    durations = [0, 3, 6, 12, 24, 36, 'all']

    for filing_type in set(filing['type'] for filing in filing_data):

        filings = {}
        for duration in durations:
            if duration == 'all':
                last_x_months_date = datetime.strptime('1900-01-01', '%Y-%m-%d')
            else:
                last_x_months_date = observation_datetime - timedelta(days=duration * 30)

            filtered_data = [filing for filing in filing_data if
                             filing['type'] == filing_type and
                             datetime.strptime(filing['date'], '%Y-%m-%d') >= last_x_months_date]

            count = len(filtered_data)
            key = f"sum_appt_{filing_type}_{duration}_months"
            filings[key] = count

        counts[filing_type] = filings

    return {'sum': counts}

def get_aggregated_filing_counts(filing_data, observation_date, aggregation='mean'):
    '''
    :param filing_data: the data that includes only the filing type, company number, and date
    :param observation_date: the observation date. we only want to count those filings whose filing date is lesser than the observation date
    :param aggregation: the aggregation method to use, either 'mean', 'median', 'min', or 'max'
    :return: the output consists of a dictionary which consists of each filing type and its aggregated count for different durations
    '''
    observation_datetime = datetime.strptime(observation_date, '%Y-%m-%d')
    counts = {}

    unique_company_numbers = set(filing['company_number'] for filing in filing_data)
    durations = [0, 3, 6, 12, 24, 36, 'all']

    for filing_type in set(filing['type'] for filing in filing_data):
        filings = {}

        for duration in durations:
            filing_counts = []

            for company_number in unique_company_numbers:
                if duration == 'all':
                    last_x_months_date = datetime.strptime('1900-01-01', '%Y-%m-%d')
                else:
                    last_x_months_date = observation_datetime - timedelta(days=duration * 30)

                filtered_data = [
                    filing for filing in filing_data if
                    filing['type'] == filing_type and
                    filing['company_number'] == company_number and
                    datetime.strptime(filing['date'], '%Y-%m-%d') >= last_x_months_date
                ]

                count = len(filtered_data)
                filing_counts.append(count)

            if aggregation == 'mean':
                aggregated_count = round(statistics.mean(filing_counts), 2)
            elif aggregation == 'median':
                aggregated_count = round(statistics.median(filing_counts), 2)
            elif aggregation == 'min':
                aggregated_count = min(filing_counts)
            elif aggregation == 'max':
                aggregated_count = max(filing_counts)
            else:
                raise ValueError("Invalid aggregation method. Please choose either 'mean', 'median', 'min', or 'max'.")

            key = f"{aggregation}_appt_{filing_type}_{duration}_months"
            filings[key] = aggregated_count

        counts[filing_type] = filings

    return {f'{aggregation}': counts}
