#!/usr/bin/env python3

import sys
from pathlib import Path
import pandas as pd
import scipy.stats as stats

# Load the data from the database
data = pd.read_csv(sys.stdin, index_col=0)

# Extract data for the 50-55 years age group
pack_year_groups = [10, 15, 20]
age_cutoff = [55, 60, 65]
outpath = Path("./reports/pack_year_analysis")
outpath.mkdir(parents=True, exist_ok=True)
# Filter out entries without pack-year history
data = data[data.pack_years.notna()]

for age in age_cutoff:
    age_group = data[(data['age'] >= 50)
                     & (data['age'] <= age)]
    age_path = outpath / f"age_50-{age}"
    age_path.mkdir(parents=True, exist_ok=True)

    for py in pack_year_groups:
        report_path = age_path / f"pack_year_summary_{py}.txt"

        # Calc the mean and range in pack years per sex, split by smoking status
        ex_smokers = age_group[age_group['ex_smoker'] == 1]
        current_smokers = age_group[age_group['current_smoker'] == 1]

        range_pack_years_ex = ex_smokers.groupby('sex')['pack_years'].agg(
            ['count', 'mean', 'std', 'min', 'max'])
        range_pack_years_ex = range_pack_years_ex.round(2)
        range_pack_years_current = current_smokers.groupby(
            'sex')['pack_years'].agg(['count', 'mean', 'std', 'min', 'max'])
        range_pack_years_current = range_pack_years_current.round(2)
        current_pack_grt_py = current_smokers[current_smokers['pack_years'] >= py].groupby('sex').size()
        current_pack_grt_py_perc = current_smokers[current_smokers['pack_years'] >= py].groupby('sex').size() / current_smokers.groupby('sex').size() * 100
        current_smokers_py_or_more_report = pd.concat([
            current_pack_grt_py, current_pack_grt_py_perc
        ],
                                                   axis=1,
                                                   keys=[
                                                       'count', 'percentage'
                                                   ])
        # Round the percentage column to two decimal places
        current_smokers_py_or_more_report[
            'percentage'] = current_smokers_py_or_more_report['percentage'].round(
                2)

        # Categorize past smokers based on how long ago they stopped smoking
        ex_smokers['years_since_quit'] = ex_smokers[
            'age'] - ex_smokers['smoking_end-age']
        ex_smokers['years_quit'] = pd.cut(ex_smokers['years_since_quit'],
                                          [0, 5, 10, 15, 20, 100],
                                          right=False,
                                          labels=[
                                              '<5 years', '5-10 years',
                                              '10-15 years', '15-20 years',
                                              '20+ years'
                                          ])

        # Calculate the pack years for each subgroup of past smokers
        pack_years_subgroup = ex_smokers.groupby([
            'sex', 'years_quit'
        ])['pack_years'].agg(['count', 'mean', 'std', 'min', 'max'])
        pack_years_subgroup = pack_years_subgroup.round(2)

        # Determine number of past smokers in each subgroup with >x pack years
        past_smokers_py_or_more = ex_smokers[
            ex_smokers['pack_years'] >= py].groupby(['sex',
                                                     'years_quit']).size()
        past_smokers_py_or_more = ex_smokers[
            ex_smokers['pack_years'] >= py].groupby(['sex', 'years_quit'])
        past_smokers_py_or_more_count = past_smokers_py_or_more.size()
        past_smokers_py_or_more_percentage = past_smokers_py_or_more_count / ex_smokers.groupby(
            ['sex', 'years_quit']).size() * 100

        # Concatenate count and percentage series horizontally
        past_smokers_py_or_more_report = pd.concat([
            past_smokers_py_or_more_count, past_smokers_py_or_more_percentage
        ],
                                                   axis=1,
                                                   keys=[
                                                       'count', 'percentage'
                                                   ])

        # Round the percentage column to two decimal places
        past_smokers_py_or_more_report[
            'percentage'] = past_smokers_py_or_more_report['percentage'].round(
                2)

        # Conduct t-tests between male and female groups for ex-smokers
        ex_smokers_males = ex_smokers[ex_smokers['sex'] ==
                                      'Male']['pack_years']
        ex_smokers_females = ex_smokers[ex_smokers['sex'] ==
                                        'Female']['pack_years']
        ttest_result_ex = stats.ttest_ind(ex_smokers_males,
                                          ex_smokers_females,
                                          equal_var=False)
        # Conduct t-tests between male and female groups for current smokers
        current_smokers_males = current_smokers[current_smokers['sex'] ==
                                                'Male']['pack_years']
        current_smokers_females = current_smokers[current_smokers['sex'] ==
                                                  'Female']['pack_years']
        ttest_result_current = stats.ttest_ind(current_smokers_males,
                                               current_smokers_females,
                                               equal_var=False)

        # Output the report
        with open(report_path, 'w') as f:
            f.write('Pack Years for Current Smokers:\n')
            f.write(range_pack_years_current.to_string())
            f.write(f'\nt-value: {round(ttest_result_current.statistic, 4)}\n')
            f.write(f'p-value: {round(ttest_result_current.pvalue, 4)}\n')
            f.write(f'\n\nCurrent Smokers with {py} Pack Years or More:\n')
            f.write(current_smokers_py_or_more_report.to_string())
            f.write('\n\nPack Years for Ex Smokers:\n')
            f.write(range_pack_years_ex.to_string())
            f.write(f'\nt-value: {round(ttest_result_ex.statistic, 4)}\n')
            f.write(f'p-value: {round(ttest_result_ex.pvalue, 4)}\n')
            f.write('\n\nPack Years for Each Subgroup of Past Smokers:\n')
            f.write(pack_years_subgroup.to_string())
            f.write(f'\n\nPast Smokers with {py} Pack Years or More:\n')
            f.write(past_smokers_py_or_more_report.to_string())
