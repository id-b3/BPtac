#!/usr/bin/env python

from pathlib import Path
import pandas as pd


def create_table(data: pd.DataFrame, bps: list, out_path: Path, group_by: str):
    """
    Create a reference table for given data based on group by values and specified bps.

    Parameters:
    data (pd.DataFrame): Input data in pandas DataFrame format.
    bps (list): List of column names for which to calculate quantiles.
    out_path (Path): Path of the output reference table csv file.
    group_by (str): Column name based on which to group the data.

    Returns:
    None

    Raises:
    None
    """
    ref_dfs = {}

    for sex in data.sex.unique():
        sex_data = data.groupby("sex").get_group(sex)
        ref_vals = sex_data.groupby(group_by)[bps].quantile(
            [0.1, 0.25, 0.5, 0.75, 0.9, 0.95])
        ref_vals = ref_vals.unstack()
        ref_vals[sex] = sex_data.groupby(group_by)[bps[0]].count()
        ref_dfs[sex] = ref_vals.T.round(3)

    ref_df = pd.concat(ref_dfs.values())
    ref_df.to_csv(str(out_path / 'reference_table.csv'))
