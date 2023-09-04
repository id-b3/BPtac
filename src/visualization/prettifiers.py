import logging
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger("BronchialParameters")

def prettify_axes(fig):
    def _prettify_label(label):
        return label.replace("bp_", "").replace("_", " ").title()

    if isinstance(fig, sns.FacetGrid):
        ax = fig.ax
    elif isinstance(fig, plt.Axes):
        ax = fig
    else:
        pass
        print("Error with plot type")

    x_label = _prettify_label(ax.get_xlabel())
    y_label = _prettify_label(ax.get_ylabel())
    ax.set_xlabel(x_label, fontsize=14)
    ax.set_ylabel(y_label, fontsize=14)
