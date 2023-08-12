import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd


def calculate_mode(x):
    if x.dtype == object:
        modes = x.str.split(';').explode().mode()
    else:
        modes = x.mode()
    return modes.iat[0] if len(modes) > 0 else np.nan


def plot_attribute_counts_bad_rate_count_type(good_officer_df, bad_officer_df, attribute_column,
                                              count_type='count_all', fig_length=12, fig_width=8, top_num_values=10):
    if count_type == 'unique':
        good_attribute_counts = good_officer_df.groupby(attribute_column)['officer_number'].nunique().astype(int)
        bad_attribute_counts = bad_officer_df.groupby(attribute_column)['officer_number'].nunique().astype(int)
        title = f'Top {top_num_values} {attribute_column.capitalize()} Counts and Bad Rate (Unique)'
    elif count_type == 'mode':
        good_officer_attribute_data = good_officer_df.copy()
        mode_per_good_officer = good_officer_attribute_data.groupby('officer_number')[attribute_column].agg(
            calculate_mode)

        bad_officer_attribute_data = bad_officer_df.copy()
        mode_per_bad_officer = bad_officer_attribute_data.groupby('officer_number')[attribute_column].agg(
            calculate_mode)

        good_attribute_counts = mode_per_good_officer.value_counts().astype(int)
        bad_attribute_counts = mode_per_bad_officer.value_counts().astype(int)
        title = f'Top {top_num_values} {attribute_column.capitalize()} Counts and Bad Rate (Mode)'
    else:
        good_attribute_counts = good_officer_df[attribute_column].value_counts().astype(int)
        bad_attribute_counts = bad_officer_df[attribute_column].value_counts().astype(int)
        title = f'Top {top_num_values} {attribute_column.capitalize()} Counts and Bad Rate (CountAll)'

    merged_counts = pd.concat([good_attribute_counts, bad_attribute_counts], axis=1)
    merged_counts.columns = ['Good Officer', 'Bad Officer']
    merged_counts = merged_counts.fillna(0)

    top_num_value = merged_counts.nlargest(top_num_values, 'Good Officer').index.tolist()

    merged_counts = merged_counts.loc[top_num_value]

    merged_counts['Bad Rate'] = merged_counts['Bad Officer'] / (
                merged_counts['Bad Officer'] + merged_counts['Good Officer'])
    merged_counts.sort_values(by='Bad Rate', inplace=True, ascending=False)

    plt.figure(figsize=(fig_length, fig_width))

    ax1 = plt.gca()
    ax2 = ax1.twinx()

    merged_counts[['Good Officer', 'Bad Officer']].plot(kind='bar', ax=ax1, color=['green', 'red'], legend=False)

    ax2.plot(ax1.get_xticks(), merged_counts['Bad Rate'], color='black', linestyle='--', marker='o', label='Bad Rate')

    for i, (good_count, bad_count, rate) in enumerate(
            zip(merged_counts['Good Officer'], merged_counts['Bad Officer'], merged_counts['Bad Rate'])):
        ax1.annotate(f'{int(good_count)}', xy=(i, good_count), xytext=(0, 5), textcoords='offset points', ha='center',
                     color='black')
        ax1.annotate(f'{int(bad_count)}', xy=(i, bad_count), xytext=(0, 5), textcoords='offset points', ha='center',
                     color='black')
        ax2.annotate(f'{rate:.2%}', xy=(i, rate), xytext=(0, 5), textcoords='offset points', ha='center')

    ax2.set_ylabel('Bad Rate (%)')
    max_bad_rate = merged_counts['Bad Rate'].max()
    ax2.set_ylim(0, max_bad_rate * 1.2)
    ax2.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))

    ax1.set_xticks(range(len(merged_counts)))
    ax1.set_xticklabels(merged_counts.index, rotation=45, ha='right', wrap=True)

    ax1.set_xlabel(attribute_column.capitalize())
    ax1.set_ylabel('Count')
    ax1.legend(['Good Officer', 'Bad Officer'], loc='upper left')
    ax2.legend(loc='upper right')

    plt.title(title)
    plt.tight_layout()
    plt.show()