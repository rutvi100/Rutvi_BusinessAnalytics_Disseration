import statistics
from datetime import datetime
from statistics import median
from hoodsio.tuin.models import CompanyTUIN
def extract_financial_data(officer_data):
    '''
    :param officer_data: officer data containing all attributes
    :return: data specific to financials
    '''
    financial_data = []

    other_financials = officer_data.get('financials', {}).get('other', {})

    for company_number, financials_list in other_financials.items():
        for financial in financials_list:
            accounts_date = financial['accounts_date']
            publication_date = financial['publication_date']
            total_assets = financial['total_assets']
            trade_creditors = financial['trade_creditors']
            current_assets = financial['current_assets']
            current_liabilities = financial['current_liabilities']
            turnover = financial['turnover']
            ebitda = financial['ebitda']
            accountant = financial['accountant']
            trade_debtors = financial['trade_debtors']
            financial_data.append({'company_number': company_number, 'accounts_date': accounts_date, 'publication_date': publication_date, 'total_assets': total_assets, 'trade_creditors': trade_creditors, 'current_assets': current_assets, 'current_liabilities': current_liabilities, 'turnover': turnover, 'ebitda': ebitda, 'accountant': accountant, 'trade_debtors': trade_debtors})

    return financial_data

def calculate_metric_to_total_assets(data, metric, aggregation='mean'):
    '''
    :param data: data specific to financials
    :param metric: the financial data column that we want to look into
    :param aggregation: the aggregation type - mean, median, min or max
    :return: returns the aggregation of the column in question w.r.t. the total assets. The data is aggregated at an officer level (by aggregating the company metric values)
    '''

    company_data = {}
    for financial_data_key in data:
        company_number = financial_data_key['company_number']
        publication_date = datetime.strptime(financial_data_key['publication_date'], '%Y-%m-%d')
        if company_number not in company_data or publication_date > datetime.strptime(company_data[company_number]['publication_date'], '%Y-%m-%d'):
            company_data[company_number] = financial_data_key

    metric_to_total_assets = []
    for financial_data_key in company_data.values():
        metric_value = financial_data_key[metric]
        total_assets = financial_data_key['total_assets']
        if metric_value is None:
            metric_value = 0
        if total_assets is None or total_assets == 0:
            #TODO: Set total_assets to 1 if it is zero - need to check this with Alex
            total_assets = 1
        metric_to_total_assets.append(metric_value / total_assets)

    if not metric_to_total_assets:
        return {f'{aggregation}_{metric}_to_total_assets': 0}

    if aggregation == 'mean':
        result = round(sum(metric_to_total_assets) / len(metric_to_total_assets), 5)
    elif aggregation == 'median':
        result = round(median(metric_to_total_assets), 5)
    elif aggregation == 'min':
        result = round(min(metric_to_total_assets), 5)
    elif aggregation == 'max':
        result = round(max(metric_to_total_assets), 5)
    else:
        raise ValueError("Invalid aggregation. Supported values are 'mean', 'median', 'min', and 'max'.")

    return {f'{aggregation}_{metric}_to_total_assets': result}

def check_financial_company_flag(financial_data, observation_date):
    observation_date = datetime.strptime(observation_date, '%Y-%m-%d')

    filtered_data_by_observation_date = [
        d for d in financial_data
        if d['publication_date'] is None or (datetime.strptime(d['publication_date'], '%Y-%m-%d') < observation_date)
    ]

    any_flag = None
    all_flag = None

    for data in filtered_data_by_observation_date:
        company_number = data['company_number']
        publication_date = data['publication_date']
        incorporation_date = None

        try:
            company = CompanyTUIN.objects.get(company_number=company_number, company_country='GB')
            incorporation_date = company.incorporation_date
        except CompanyTUIN.DoesNotExist:
            incorporation_date = None

        if publication_date is None:
            flag = 0  # If publication_date is None, assign flag as 0 (data not published)
        elif datetime.strptime(publication_date, '%Y-%m-%d') < observation_date:
            flag = 1
        else:
            if incorporation_date is None:
                flag = None
            elif incorporation_date < observation_date:
                flag = 0
            else:
                flag = None

        if flag is not None:
            if any_flag is None:
                any_flag = flag
            else:
                any_flag |= flag

            if all_flag is None:
                all_flag = flag
            else:
                all_flag &= flag

    return {'any_financial_company_flag': any_flag, 'all_financial_company_flag': all_flag}

def calculate_time_to_publish_accounts(financial_data, aggregation='mean'):
    '''
    :param financial_data: data specific to financials
    :param aggregation: the aggregation type - mean, median, min or max
    :return: returns the aggregated time to publish financials at an officer level (aggregates all the company level values for each officer)
    '''
    filtered_data = {}
    for data in financial_data:
        company_number = data['company_number']
        publication_date = data['publication_date']
        accounts_date = datetime.strptime(data['accounts_date'], '%Y-%m-%d')

        if publication_date is not None:
            publication_date = datetime.strptime(publication_date, '%Y-%m-%d')
            if company_number not in filtered_data or (filtered_data[company_number]['publication_date'] is not None and filtered_data[company_number]['publication_date'] < publication_date):
                filtered_data[company_number] = {'publication_date': publication_date, 'accounts_date': accounts_date}

    time_to_publish = []
    for data in filtered_data.values():
        time = (data['publication_date'] - data['accounts_date']).days
        time_to_publish.append(time)

    if aggregation == 'mean':
        result = statistics.mean(time_to_publish) if time_to_publish else 0
    elif aggregation == 'median':
        result = statistics.median(time_to_publish) if time_to_publish else 0
    elif aggregation == 'min':
        result = min(time_to_publish) if time_to_publish else 0
    elif aggregation == 'max':
        result = max(time_to_publish) if time_to_publish else 0
    else:
        raise ValueError('Invalid aggregation method. Must be one of: mean, median, min, max.')

    return {f'{aggregation}_time_to_publish_financials': round(result, 2)}


