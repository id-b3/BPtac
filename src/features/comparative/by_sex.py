#!/usr/bin/env python3

import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def compare(data, parameters, out_path):
    # Function to perform one-way ANOVA and Tukey's test
    def _perform_anova_and_tukey(data, parameter):
        # One-way ANOVA
        anova_result = stats.f_oneway(
            data[data["smoking_status"] == "current_smoker"][parameter],
            data[data["smoking_status"] == "never_smoker"][parameter],
            data[data["smoking_status"] == "ex_smoker"][parameter],
        )

        # Check if ANOVA is significant
        if anova_result.pvalue < 0.05:
            # Perform Tukey's test
            tukey = pairwise_tukeyhsd(
                endog=data[parameter],
                groups=data["smoking_status"],
                alpha=0.05,
            )
            return (True, anova_result, tukey)
        else:
            return (False, anova_result, None)

    # Initialize results table
    results = []

    # Perform tests for each sex and parameter
    for sex in ["Male", "Female"]:
        sex_df = data[data["sex"] == sex]
        for param in parameters:
            param_df = sex_df.dropna(subset=[param])
            significant, anova, tukey = _perform_anova_and_tukey(param_df, param)
            result = {
                "sex": sex,
                "parameter": param,
                "anova_f": anova.statistic,
                "anova_p": anova.pvalue,
                "significant": significant,
            }
            if significant:
                group1, group2 = tukey._multicomp.pairindices
                for g1, g2, pvalue, meandiff in zip(
                    group1, group2, tukey.pvalues, tukey.meandiffs
                ):
                    pair = (tukey.groupsunique[g1], tukey.groupsunique[g2])
                    result[f"pvalue_{pair[0]}_vs_{pair[1]}"] = pvalue
                    result[f"meandiff_{pair[0]}_vs_{pair[1]}"] = meandiff

            results.append(result)

    # Convert results to DataFrame and save as CSV
    results_df = pd.DataFrame(results)
    results_df = results_df.round(4)
    results_df.to_csv((out_path / "sex_differences.csv"), index=False)
