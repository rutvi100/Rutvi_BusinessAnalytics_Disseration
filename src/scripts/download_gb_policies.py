from hoodsio.contorta.models import Policy
from datetime import datetime
from django.db.models import F
import sys
import pandas as pd
import os

from pathlib import Path

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())

from src.utils.constants import CONFIG_DIR
import src.utils.load_params

loader = src.utils.load_params
params = loader.load_params(CONFIG_DIR / "global" / "dvc_params.yaml")


def get_historical_policies(most_recent_policy_date):
    """
    Get all GB policies that are younger than most_recent_policy_date

    :param most_recent_policy_date: this will be the date of the most recent policy
    :return: returns the historical policies
    """

    policies = Policy.objects.filter(
        quote__transaction__debtor__country="GB",
        quote__created__lt=most_recent_policy_date,
    ).annotate(debtor_id=F("quote__transaction__debtor"))

    historical_policies_list = []

    for pol in policies:
        historical_policies = pol.history.all()
        historical_policies_list.append(historical_policies)

    return historical_policies_list


def get_gb_policies_status_date(historical_policy_list):
    """
    For each historical policy, fetch relevant data to label

    :param historical_policy_list: takes the input of the previous function
    :return: returns a dataframe containing the policies
    """

    policy_data_list = []

    for historical_policies in historical_policy_list:
        for historical_policy in historical_policies:
            id_value = historical_policy.id
            history_date = historical_policy.history_date
            quote = historical_policy.quote.id
            status = historical_policy.status
            debtor_id = historical_policy.quote.transaction.debtor_id

            policy_policy_data_list = {
                "id": id_value,
                "history_date": history_date,
                "quote": quote,
                "status": status,
                "debtor_id": debtor_id,
            }
            policy_data_list.append(policy_policy_data_list)

    return pd.DataFrame(policy_data_list)


if __name__ == "__main__":
    from src.utils.constants import LOG_NAME, LOG_LEVEL, LOG_DIR, CONFIG_DIR
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    # We are downloading all the GB policies so that we can label them and see which companies were labelled as bad
    most_recent_policy_date = datetime.strptime(
        open(params["DATE_PNP_DATASET_LATEST_POLICY"], "r").read(), "%Y-%m-%d"
    ).date()

    logger.info(
        f"Filtering historical policies for most_recent_policy_date: {most_recent_policy_date}"
    )

    historical_policies_list = get_historical_policies(most_recent_policy_date)

    get_gb_policies_status_date(historical_policies_list).to_csv(
        params["ALL_GB_POLICIES"], index=False
    )
