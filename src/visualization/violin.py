#!/usr/bin/env python3

import seaborn as sns
import matplotlib.pyplot as plt

from .prettifiers import prettify_axes


def make_plots(data, bps, out_path):
    out_path = out_path / "violin"
    out_path.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid")
    for param in bps:
        fig = sns.violinplot(data=data,
                             x="smoking_status",
                             y=param,
                             hue="sex",
                             split=True,
                             inner="quart",
                             linewidth=1.5,
                             palette={
                                 "Male": "b",
                                 "Female": "salmon"
                             })
        sns.despine(left=True)
        prettify_axes(fig)
        fig.get_figure().savefig(f"{str(out_path / param)}_violin.png", dpi=300)
        plt.close()
