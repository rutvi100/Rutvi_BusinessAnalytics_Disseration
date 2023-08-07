import logging
import os
import sys

import pandas as pd

logging.basicConfig(level=logging.INFO)

from pathlib import Path

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())

import src.utils.load_params
from src.utils.constants import CONFIG_DIR

loader = src.utils.load_params
params = loader.load_params(CONFIG_DIR / "global" / "dvc_params.yaml")

GOOD_STATUSES = {"paid", "late", "at_claims", "active"}
BAD_STATUSES = {"under_collection"}


#def drop_rows_by_status(df, status):
#    """
#    We want to drop the policies that have the status of `status`
#    :param df: Takes the dataframe as the input which contains the downloaded gb policies
#    :param status: status of the policy
#    :return: returns all rows except the input status of the function
#    """
#    df.drop(df[df["status"] == status].index, inplace=True)



def drop_rows_by_current_status_dates(df, status):
    """
    We want to drop the policies that only have the current status of `status`
    :param df: Takes the dataframe as the input which contains the downloaded gb policies
    :param status: status of the policy
    :return: drops all policies if their current status matches the status of the input parameter
    """
    max_dates = df.groupby("id")["history_date"].transform("max")

    current_status_ids = df[
        (df["status"] == status) & (df["history_date"] == max_dates)
    ]["id"].unique()
    df.drop(df[df["id"].isin(current_status_ids)].index, inplace=True)


def drop_policy_rows_if_ever_status(df, status):
    """
    We want to drop the policies if they ever had the input `status`
    :param df: Takes the dataframe as the input which contains the downloaded gb policies
    :param status: status of the policy
    :return: drops all policies that have had the status of cancelled
    """
    # Find IDs that have the input status
    ids_with_status = df[df["status"] == status]["id"].unique()

    # Drop all rows with IDs that have the input status
    df.drop(df[df["id"].isin(ids_with_status)].index, inplace=True)


def filter_not_collectable(df, status="not_collectable"):
    """
    If policy created date <= certain specified date below and status = input status, drop those policies. Otherwise, do not drop and label as bad.
    :param df: Takes the dataframe as the input which contains the downloaded gb policies
    :param status: status of the policy
    :return: drop policies if created date <= certain specified date below and status = input status
    """
    date_threshold = pd.Timestamp("2022-01-01").date()

    # TODO why doesn't format="mixed" work
    df["history_date"] = pd.to_datetime(
        df["history_date"]  # , format="mixed", dayfirst=True
    ).dt.date

    # Get the IDs that have the status 'not_collectable'
    not_collectable_ids = df[df["status"] == status]["id"].unique()

    # Filter rows based on status and created conditions
    df.drop(
        df[
            (df["history_date"] <= date_threshold) & df["id"].isin(not_collectable_ids)
        ].index,
        inplace=True,
    )


def get_policy_status(status):
    """
    :param status: status of the policy
    :return: maps the status to a broader group of statuses
    """
    if status in ["paid", "paid_distributor"]:
        return "paid"
    elif status in ["late", "late_can_handover", "pay_installments", "elapsed"]:
        return "late"
    elif status in [
        "claim_submitted",
        "claim_approved",
        "recovery_underway",
        "recovery_complete",
        "recovery_rejected",
        "recovery_installments",
        "claim_rejected",
        "dispute_pursual",
    ]:
        return "at_claims"
    elif status in [
        "under_collection",
        "under_collection_installments",
        "under_collection_dispute_solved",
        "not_collectable",
        "claim_rejected",
    ]:
        return "under_collection"
    elif status in [
        "active",
    ]:
        return "active"
    else:
        return "unknown"


def get_label(mapped_status, logger):
    """
    Return label given a mapped status
    """

    if mapped_status in GOOD_STATUSES:
        return 0
    if mapped_status in BAD_STATUSES:
        return 1
    else:
        logger.warning(f"!!!! {mapped_status} cannot be labelled !!!!")

def label_entire_policy(df, policy_id):
    """
    Label all rows of a policy with the given policy_id as 1
    :param df: Dataframe containing the policies
    :param policy_id: ID of the policy to label
    """
    df.loc[df["id"] == policy_id, "label"] = 1

def label_policies_using_status(df, logger):
    """
    :param df: dataframe on downloaded gb policies
    :return: returns the label based on the mappings we assigned to the policies
    """
    df["mapped_status"] = df["status"].apply(get_policy_status)

    unknown_count = df[df["mapped_status"] == "unknown"].shape[0]
    if unknown_count > 0:
        logger.info(f"Number of policies with unknown status: {unknown_count}")
        logger.info("We are dropping the policies with an unknown status")
        unknown_policies = df[df["mapped_status"] == "unknown"]
        logger.info("Unknown status policies:")
        logger.info(unknown_policies)

    df.drop(df[df["mapped_status"] == "unknown"].index, inplace=True)

    df["label"] = df.apply(lambda row: get_label(row["mapped_status"], logger), axis=1)

    assert str(df.label.dtype) == "int64"

    policies_with_label_1 = df[df["label"] == 1]["id"].unique()
    for policy_id in policies_with_label_1:
        label_entire_policy(df, policy_id)

def get_observation_dates(gb_policies):

    gb_policies["history_date"] = pd.to_datetime(
        gb_policies["history_date"]
    )  # Convert history_date column to datetime if it's not already
    active_rows = gb_policies[gb_policies["status"] == "active"]
    earliest_active_rows = active_rows.groupby("id")["history_date"].idxmin()
    result = gb_policies.loc[earliest_active_rows]
    result["history_date"] = result.history_date.dt.date
    earliest_company_observation_date = result.loc[
        gb_policies.groupby("debtor_id")["history_date"].idxmin()
    ]
    earliest_company_observation_date = earliest_company_observation_date[
        ["id", "history_date", "debtor_id"]
    ]
    earliest_company_observation_date.columns = [
        "policy",
        "observation_date",
        "company",
    ]
    return earliest_company_observation_date


if __name__ == "__main__":
    from src.utils.constants import CONFIG_DIR, LOG_DIR, LOG_LEVEL, LOG_NAME
    from src.utils.custom_logging import get_logger

    script_name = os.path.splitext(os.path.basename(__file__))[0]

    logger = get_logger(LOG_NAME, LOG_LEVEL, LOG_DIR)

    logger.info(f"Running Step {script_name}")

    gb_policies = pd.read_csv(params["ALL_GB_POLICIES"])

    earliest_company_observation_date = get_observation_dates(
        gb_policies.copy(deep=True)
    )
    earliest_company_observation_date.to_csv(
        params["EARLIEST_CO_OBSERVATION"], index=False
    )

    # TODO in the future we want this function to remove not yet mature policies when the labelling is carried out
    #drop_rows_by_status

    drop_policy_rows_if_ever_status(gb_policies, "not_collectable_dispute")
    drop_policy_rows_if_ever_status(gb_policies, "other")
    drop_rows_by_current_status_dates(gb_policies, "elapsed")
    drop_policy_rows_if_ever_status(gb_policies, "cancelled")
    filter_not_collectable(gb_policies)
    label_policies_using_status(gb_policies, logger)

    gb_policies.to_csv(params["LABELED_GB_POLICIES"], index=False)
