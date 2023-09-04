#!/usr/bin/env python3

import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import seaborn as sns
import statsmodels.api as sm
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

from src.data.subgroup import get_healthy

# Define command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("input_csv", help="Input CSV file name")
parser.add_argument("parameters",
                    help="Comma-separated list of parameter names")
parser.add_argument("output", help="Output CSV file name")
parser.add_argument("--healthy",
                    action="store_true",
                    help="Only include 'healthy general population' group")

# Parse arguments
args = parser.parse_args()

# Read input CSV file
data = pd.read_csv(args.input_csv, low_memory=False)

# Filter by smoking status if healthy flag is set
if args.healthy:
    data = get_healthy(data)
# Split parameter names into a list
params = args.parameters.split(",")

# Create empty lists to store results
results = []

data['years_since_quit'] = data['age'] - data['smoking_end-age']
data['years_quit'] = pd.cut(data['years_since_quit'], [0, 5, 10, 15, 20, 100],
                            right=False,
                            labels=[
                                '<5 years', '5-10 years', '10-15 years',
                                '15-20 years', '20+ years'
                            ])
data = data[data.smoking_status == 'ex_smoker']

# Loop over each parameter and calculate Pearson's correlation coefficient and R-squared
for param in params:
    data_param = data.dropna(
        subset=[param, 'years_since_quit', 'pack_year_categories'])

    independent_vars = ['sex', 'age', 'bmi', 'pack_year_categories', 'years_since_quit']

    formula = f"{param} ~ {' + '.join(independent_vars)}"
    model = sm.formula.ols(formula=formula, data=data_param).fit()
    with open(str(Path(args.output).parent / f"cessation_{param}.txt"), "w") as f:
        f.write(model.summary().as_text())

    # X = data_param[['years_since_quit', 'age']].values
    # X = np.concatenate((pd.get_dummies(data_param.sex).values, X, pd.get_dummies(data_param.pack_year_categories).values), axis=1)
    # y = data_param[[param]].values
    # pearson, _ = pearsonr(X.T[0], y.T[0])
    rsquared = model.rsquared
    pval = round(model.f_pvalue, 4)

    # Create a dictionary to store results
    result = {
        'Parameter': param,
        # 'Pearson Correlation': pearson,
        'R-squared': rsquared,
        'P-value': pval
    }
    results.append(result)

    fig, ax = plt.subplots(figsize=(12, 6))

    x_values = np.linspace(data["years_since_quit"].min(), data["years_since_quit"].max(), 100)
    y_values = model.params['Intercept'] + model.params['sex[T.Male]'] + (60 * model.params['age']) + (24 * model.params['bmi']) + model.params['years_since_quit'] * x_values

    ax.plot(x_values, y_values, color='red')
    # sns.regplot(x=data_param['years_since_quit'],
    #             y=model.predict(sm.add_constant(X)),
    #             scatter=False,
    #             ax=ax)
    ax.set_ylim(data_param[param].min(), data_param[param].max())
    ax.set_title(f"{param} with smoking cessation")
    ax.set_xlabel("Duration of smoking cessation")
    ax.set_ylabel(param)
    plt.tight_layout()
    fig.savefig(f"./reports/figures/regression/smoking_cessation_{param}.jpg",
                dpi=300)

# Create a pandas DataFrame from the results dictionary
results_data = pd.DataFrame.from_dict(results)
results_data = results_data.round(2)

# Output results to a CSV file
results_data.to_csv(args.output, index=False)
