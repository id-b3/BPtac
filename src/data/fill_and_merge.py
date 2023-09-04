#!/usr/bin/env python

import sys
from pathlib import Path
import numpy as np
import pandas as pd

df = pd.read_csv(sys.stdin, index_col=0)
outpath = Path("./data/interim/")

# ------ PARTICIPANT CHARACTERISTICS
# Fill in missing sex values, drop the other columns
df['gender'].fillna(df['gender_first'].fillna(df['gender_first2']),
                    inplace=True)
df['gender'] = df['gender'].str.title()
df['age_at_scan'].replace('#NUM!', np.nan, inplace=True)
df['age_at_scan'].fillna(df['age'], inplace=True)
df['age_at_scan'] = df['age_at_scan'].astype(float)
df.drop(['age'], axis=1, inplace=True)
df['weight_at_scan'].fillna(df['bodyweight_kg_all_m_1_max2'].fillna(
    df['bodyweight_kg_all_m_1_max'].fillna(df['bodyweight_current_adu_q_1'])),
                            inplace=True)
df['length_at_scan'].fillna(df['bodylength_cm_all_m_1_max2'], inplace=True)
df['length_at_scan'].fillna(df['bodylength_cm_all_m_1_max'], inplace=True)
df['length_at_scan'] = df['length_at_scan'] / 100

df = df.rename(
    columns={
        'gender': 'sex',
        'age_at_scan': 'age',
        'weight_at_scan': 'weight',
        'length_at_scan': 'height'
    })

# Calculate BMI
df['bmi'] = df['weight'] / (df['height'])**2

df.drop([
    'gender_first', 'gender_first2', 'bodyweight_kg_all_m_1_max2',
    'bodyweight_kg_all_m_1_max', 'bodyweight_current_adu_q_1',
    'bodylength_cm_all_m_1_max2', 'bodylength_cm_all_m_1_max'
],
        axis=1,
        inplace=True)

# Calc mean BPs
df['bp_wap_avg'] = df[['bp_wap_3', 'bp_wap_4', 'bp_wap_5']].mean(axis=1)
df['bp_la_avg'] = df[['bp_la_3', 'bp_la_4', 'bp_la_5']].mean(axis=1)
df['bp_wt_avg'] = df[['bp_wt_3', 'bp_wt_4', 'bp_wt_5']].mean(axis=1)
df['bp_ir_avg'] = df[['bp_ir_3', 'bp_ir_4', 'bp_ir_5']].mean(axis=1)
df['bp_or_avg'] = df[['bp_or_3', 'bp_or_4', 'bp_or_5']].mean(axis=1)

# Create age categories
age_label_5 = [
    '45-50', '50-55', '55-60', '60-65', '65-70', '70-75', '75-80',
    '80+'
]
age_cut_5 = np.linspace(45, 80, 8)
age_cut_5 = np.append(age_cut_5, 100)

df['age_5yr'] = pd.cut(df['age'],
                       bins=age_cut_5,
                       labels=age_label_5,
                       right=False)

age_label_10 = ['45-54', '55-64', '65-74', '75-84', '85+']
age_cut_10 = np.linspace(45, 85, 5)
age_cut_10 = np.append(age_cut_10, 100)

df['age_10yr'] = pd.cut(df['age'],
                        bins=age_cut_10,
                        labels=age_label_10,
                        right=False)

# ------ SMOKING
# Smoking merge and fill
df['never_smoker'] = df['never_smoker_adu_c_12'].fillna(
    df['never_smoker_adu_c_1'].fillna(df['never_smoker_adu_c_12_2']))

df['ever_smoker'] = df['ever_smoker_adu_c_22'].fillna(
    df['ever_smoker_adu_c_2'].fillna(df['ever_smoker_adu_c_22_2'].fillna(
        df['ever_smoker_adu_c_22_3'].fillna(df['ever_smoker_adu_c_22_4']))))

df['current_smoker'] = df['current_smoker_adu_c_22'].fillna(
    df['current_smoker_adu_c_2'].fillna(df['current_smoker_adu_c_22_2'].fillna(
        df['current_smoker_adu_c_22_3'].fillna(
            df['current_smoker_adu_c_22_4']))))

df['ex_smoker'] = df['ex_smoker_adu_c_22'].fillna(
    df['ex_smoker_adu_c_2'].fillna(df['ex_smoker_adu_c_22_2'].fillna(
        df['ex_smoker_adu_c_22_3'].fillna(df['ex_smoker_adu_c_22_4']))))

df['pack_years'] = df['packyears_cumulative_adu_c_22'].fillna(
    df['packyears_cumulative_adu_c_2'].fillna(
        df['packyears_cumulative_adu_c_22_2'].fillna(
            df['packyears_cumulative_adu_c_22_3'].fillna(
                df['packyears_cumulative_adu_c_22_4']))))

df['smoking_end-age'] = df['smoking_endage_adu_c_22'].fillna(
    df['smoking_endage_adu_c_2'].fillna(df['smoking_endage_adu_c_22_2'].fillna(
        df['smoking_endage_adu_c_22_3'].fillna(
            df['smoking_endage_adu_c_22_4']))))

df['smoking_start-age'] = df['smoking_startage_adu_c_22'].fillna(
    df['smoking_startage_adu_c_2'].fillna(
        df['smoking_startage_adu_c_22_2'].fillna(
            df['smoking_startage_adu_c_22_3'].fillna(
                df['smoking_startage_adu_c_22_4']))))

df['smoking_duration'] = df['smoking_duration_adu_c_22'].fillna(
    df['smoking_duration_adu_c_2'].fillna(
        df['smoking_duration_adu_c_22_2'].fillna(
            df['smoking_duration_adu_c_22_3'].fillna(
                df['smoking_duration_adu_c_22_4']))))

# Calculate missing pack years
duration = df['smoking_end-age'].fillna(df['age']) - df['smoking_start-age']
mask = df['smoking_start-age'].notna() & df['smoking_duration'].isna()
df.loc[mask, 'smoking_duration'] = duration[mask]

df['max_cig_freq'] = df[[
    'cigarettes_frequency_adu_q_1_a', 'cigarettes_frequency_adu_q_1',
    'cigarettes_frequency_adu_c_2'
]].max(axis=1)
df['max_ciga_freq'] = df[[
    'cigarillos_frequency_adu_c_2', 'cigarillos_frequency_adu_q_1',
    'cigarillos_frequency_adu_q_1_a'
]].max(axis=1)
df['max_cigar_freq'] = df[[
    'cigars_frequency_adu_c_2', 'cigars_frequency_adu_q_1',
    'cigars_frequency_adu_q_1_a'
]].max(axis=1)
df['max_other_freq'] = df[[
    'pipetobacco_frequency_adu_c_2', 'pipetobacco_frequency_adu_q_1',
    'pipetobacco_frequency_adu_q_1_a'
]].max(axis=1)

df['total_freq_calc'] = df['max_cig_freq'] + df['max_ciga_freq'] + df[
    'max_cigar_freq'] + df['max_other_freq']

df['total_frequency'] = df['total_frequency_adu_c_12'].fillna(
    df['total_frequency_adu_c_1'].fillna(df['total_freq_calc']))

df.loc[df.total_frequency == 0, 'total_frequency'] = np.nan

df['pack_years_calc'] = df['smoking_duration'] * df['total_frequency'] / 20
df['pack_years'].fillna(df['pack_years_calc'], inplace=True)

# Fill never smoker = False if any of the others is True
df.loc[df.never_smoker.isna() & (~df.current_smoker.isna() & df.current_smoker)
       | (df.ever_smoker.notna() & df.ever_smoker) |
       (df.ex_smoker.notna() & df.ex_smoker), ['never_smoker']] = False

# Fill never smoker = True if ALL the others are False
try:
    df.loc[(df.never_smoker.isna() & df.current_smoker.notna()
            & df.ever_smoker.notna() & df.ex_smoker.notna()) &
           (~df.current_smoker & ~df.ex_smoker & ~df.ever_smoker),
           ['never_smoker']] = True
except TypeError:
    print("All values False for smoking status, filling Never Smoker as True")
    df.loc[(df.never_smoker.isna() & df.current_smoker.notna()
            & df.ever_smoker.notna() & df.ex_smoker.notna()),
           ['never_smoker']] = True


# Create "smoking_status" variable for easier separation
def get_smoking_status(row):
    if row["current_smoker"] is True:
        return "current_smoker"
    if row["ex_smoker"] is True:
        return "ex_smoker"
    if row["never_smoker"] is True:
        return "never_smoker"
    else:
        return None


df["smoking_status"] = df.apply(get_smoking_status, axis=1)

# Split pack-years to categories
py_labels = ['0', '1-10', '10-20', '20+']
py_categories = [-5, 0, 10, 20, 100]

df['pack_year_categories'] = pd.cut(df['pack_years'],
                                    bins=py_categories,
                                    labels=py_labels,
                                    right=False)
df['pack_year_categories'].fillna("0", inplace=True)

df.drop([
    'ever_smoker_adu_c_2', 'ever_smoker_adu_c_22', 'ever_smoker_adu_c_22_2',
    'ever_smoker_adu_c_22_3', 'ever_smoker_adu_c_22_4', 'never_smoker_adu_c_1',
    'never_smoker_adu_c_12', 'never_smoker_adu_c_12_2',
    'current_smoker_adu_c_2', 'current_smoker_adu_c_22',
    'current_smoker_adu_c_22_2', 'current_smoker_adu_c_22_3',
    'current_smoker_adu_c_22_4', 'ex_smoker_adu_c_2', 'ex_smoker_adu_c_22',
    'ex_smoker_adu_c_22_2', 'ex_smoker_adu_c_22_3', 'ex_smoker_adu_c_22_4',
    'packyears_cumulative_adu_c_2', 'packyears_cumulative_adu_c_22',
    'packyears_cumulative_adu_c_22_2', 'packyears_cumulative_adu_c_22_3',
    'packyears_cumulative_adu_c_22_4', 'smoking_endage_adu_c_2',
    'smoking_endage_adu_c_22', 'smoking_endage_adu_c_22_2',
    'smoking_endage_adu_c_22_3', 'smoking_endage_adu_c_22_4',
    'smoking_duration_adu_c_2', 'smoking_duration_adu_c_22',
    'smoking_duration_adu_c_22_2', 'smoking_duration_adu_c_22_3',
    'smoking_duration_adu_c_22_4', 'cigarettes_frequency_adu_q_1',
    'cigarettes_frequency_adu_q_1_a', 'cigarettes_frequency_adu_c_2',
    'cigars_frequency_adu_q_1_a', 'cigars_frequency_adu_q_1',
    'cigars_frequency_adu_c_2', 'cigarillos_frequency_adu_q_1_a',
    'cigarillos_frequency_adu_q_1', 'cigarillos_frequency_adu_c_2',
    'pipetobacco_frequency_adu_q_1_a', 'pipetobacco_frequency_adu_q_1',
    'pipetobacco_frequency_adu_c_2', 'total_frequency_adu_c_1',
    'total_frequency_adu_c_12', 'smoking_startage_adu_c_2',
    'smoking_startage_adu_c_22', 'smoking_startage_adu_c_22_2',
    'smoking_startage_adu_c_22_3', 'smoking_startage_adu_c_22_4',
    'max_other_freq', 'max_cigar_freq', 'max_ciga_freq', 'max_cig_freq',
    'total_freq_calc', 'pack_years_calc'
],
        axis=1,
        inplace=True)

# ------ RESPIRATORY DISEASE
df['copd_diagnosis'] = df['copd_presence_adu_q_2'].fillna(
    df['copd_presence_adu_q_1'].fillna(
        df['spirometry_copd_all_q_1_max'].fillna(df['elon_copd_adu_q_13'])))

df['asthma_diagnosis'] = df['asthma_diagnosis_adu_q_1'].fillna(
    df['spirometry_astma_all_q_1_max'].fillna(
        df['spirometry_astma_all_q_1_max2'].fillna(
            df['elon_asthma_adu_q_06'])))

df['cancer_type'] = df['cancer_type_adu_q_1'].fillna(df['cancer_type_adu_q_2'])

df['copd_diagnosis'].replace([1, 2], ['True', 'False'], inplace=True)

df['asthma_diagnosis'].replace([1, 2], ['True', 'False'], inplace=True)

df['breathing_problems_adu_q_1'].replace([1, 2], ['BREATHING', 'False'],
                                         inplace=True)

df['coughing_presence_adu_q_1'].replace([1, 2], ['COUGHING', 'False'],
                                        inplace=True)

df['wheezing_presence_adu_q_1'].replace([1, 2], ['WHEEZE', 'False'],
                                        inplace=True)

df['elon_wheeze_adu_q_01'].replace([1, 2], ['WHEEZE', 'False'], inplace=True)

df['resp_other'] = df['wheezing_presence_adu_q_1'].fillna(
    df['elon_wheeze_adu_q_01'].fillna(df['coughing_presence_adu_q_1'].fillna(
        df['breathing_problems_adu_q_1'])))

df.drop([
    'copd_presence_adu_q_1', 'copd_presence_adu_q_2',
    'spirometry_copd_all_q_1_max', 'spirometry_astma_all_q_1_max',
    'spirometry_astma_all_q_1_max2', 'elon_copd_adu_q_13',
    'elon_asthma_adu_q_06', 'asthma_diagnosis_adu_q_1', 'cancer_type_adu_q_1',
    'cancer_type_adu_q_2', 'breathing_problems_adu_q_1',
    'coughing_presence_adu_q_1', 'wheezing_presence_adu_q_1',
    'elon_wheeze_adu_q_01'
],
        inplace=True,
        axis=1)

# ------ SPIROMETRY
df['fev1'] = df['spirometry_fev1_all_m_1_max2'].fillna(
    df['spirometry_fev1_all_m_1_max'])

df['fvc'] = df['spirometry_fvc_all_m_1_max2'].fillna(
    df['spirometry_fvc_all_m_1_max'])

df['fev1_pp'] = df['fev1_percpredicted_all_c_1_max2'].fillna(
    df['fev1_percpredicted_all_c_1_max'])

df['fev1fvc_lln'] = df['fev1fvc_lowerlimit_all_c_1_max2'].fillna(
    df['fev1fvc_lowerlimit_all_c_1_max'])

df['fev1_fvc'] = df.fev1 / df.fvc

df.drop([
    'spirometry_fev1_all_m_1_max2', 'spirometry_fev1_all_m_1_max',
    'spirometry_fvc_all_m_1_max', 'spirometry_fvc_all_m_1_max2',
    'fev1_percpredicted_all_c_1_max2', 'fev1_percpredicted_all_c_1_max',
    'fev1fvc_lowerlimit_all_c_1_max2', 'fev1fvc_lowerlimit_all_c_1_max',
    'fev1_lowerlimit_all_c_1_max2', 'fev1_lowerlimit_all_c_1_max',
    'fvc_lowerlimit_all_c_1_max2', 'fvc_lowerlimit_all_c_1_max'
],
        inplace=True,
        axis=1)

# ------ COPD GOLD Staging
# GOLD 0: FEV1/FVC > fev1fvc_lln
# GOLD 1: FEV1/FVC < fev1fvc_lln & fev1_pp > 80
# GOLD 2: FEV1/FVC < fev1fvc_lln & fev1_pp 50-80
# GOLD 3: FEV1/FVC < fev1fvc_lln & fev1_pp 50-30
# GOLD 4: FEV1/FVC < fev1fvc_lln & fev1_pp < 30

criteria = [
    ((df.fev1_pp >= 80) & (df.fev1_fvc < df.fev1fvc_lln)),
    ((df.fev1_pp < 80) & (df.fev1_pp >= 50) & (df.fev1_fvc < df.fev1fvc_lln)),
    ((df.fev1_pp < 50) & (df.fev1_pp >= 30) & (df.fev1_fvc < df.fev1fvc_lln)),
    ((df.fev1_pp < 30) & (df.fev1_fvc < df.fev1fvc_lln))
]

goldstg = ("GOLD-1", "GOLD-2", "GOLD-3", "GOLD-4")
df["GOLD_stage"] = np.select(criteria, goldstg)

df.loc[df.bp_leak_score == -1, 'bp_leak_score'] = np.nan
df.loc[df.bp_segmental_score == -1, 'bp_segmental_score'] = np.nan
df.loc[df.bp_subsegmental_score == -1, 'bp_subsegmental_score'] = np.nan

# ------ SAVE DF
df = df.round(3)
df.to_csv(str(outpath / "bp_db_all.csv"))
