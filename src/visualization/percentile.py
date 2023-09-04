#!/usr/bin/env python3

import logging

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm

from .prettifiers import prettify_axes

logger = logging.getLogger("BronchialParameters")

def make_plots(data, bps, out_path):
    out_path = out_path / "percentile"
    out_path.mkdir(parents=True, exist_ok=True)

    logger.info("Creating percentile plots")
    logger.info(f"Output directory: {out_path}")

    # Create age categories
    age_label_2 = [
        40,
        42,
        44,
        46,
        48,
        50,
        52,
        54,
        56,
        58,
        60,
        62,
        64,
        66,
        68,
        70,
        72,
        74,
        76,
        78,
        80,
        82,
        84,
    ]
    age_cut_2 = np.linspace(40, 88, 23)
    age_cut_2 = np.append(age_cut_2, 100)

    data["age_2yr"] = pd.cut(data["age"],
                             bins=age_cut_2,
                             labels=age_label_2,
                             right=False)

    sns.set_theme(style="whitegrid")

    age_dict = {"45-50": 47.5, "50-55": 52.5, "55-60": 57.5, "60-65": 62.5, "65-70": 67.5, "70-75": 72.5, "75-80": 77.5, "80+": 85}
    data.replace({"age_5yr": age_dict}, inplace=True)

    for param in tqdm(bps):
        for sex in ["Male", "Female"]:
            ylims = [data[data.sex == sex][param].quantile(0.025), data[data.sex == sex][param].quantile(0.975)]
            for sm_stat in ["never_smoker", "ex_smoker", "current_smoker"]:
                percentiles = (data[(data["smoking_status"] == sm_stat)
                                    & (data["sex"] == sex)].groupby(
                                        "age_5yr")[param].quantile(
                                            [0.1, 0.3, 0.5, 0.7,
                                             0.9]).reset_index())
                percentiles = percentiles.rename(
                    columns={"level_1": "Percentile"})
                percentiles.Percentile = percentiles["Percentile"].apply(
                    lambda x: f"{x * 100:.0f}%")

                fig = sns.lmplot(
                    data=percentiles,
                    x="age_5yr",
                    y=param,
                    hue="Percentile",
                    scatter=False,
                    truncate=False,
                    palette=sns.color_palette([
                        "deepskyblue", "mediumseagreen", "green", "orange",
                        "red"
                    ]),
                    ci=None,
                    # order=2,
                    robust=True,
                    line_kws={"alpha": 0.5},
                )

                prettify_axes(fig)

                sns.move_legend(fig,
                                "lower center",
                                bbox_to_anchor=(0.5, 1.0),
                                ncol=5,
                                title=None,
                                frameon=False)

                # Additional customization of the x-axis
                fig.set(ylim=ylims, xlim=[45, 85])
                plt.xlabel("Age")
                plt.title(f"{sex.title()} {sm_stat.replace('_', ' ').title()}")
                plt.tight_layout()
                fig.savefig(f"{str(out_path / param)}_{sex}_{sm_stat}.png",
                            dpi=300)
                plt.close()
