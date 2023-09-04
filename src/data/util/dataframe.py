import pandas as pd


def get_group(df, group: str="healthy"):
    """
    This function takes a pandas DataFrame as input and returns
    a subset of the DataFrame containing healthy individuals.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data to filter

    Returns:
    pandas.DataFrame: A subset of the original DataFrame containing
                      individuals who meet the filter criteria
    """

    healthy_mask = (
        (df.GOLD_stage == "0")
        & (df.copd_diagnosis == False)
        & (df.asthma_diagnosis == False)
        & (df.cancer_type != "LONGKANKER")
        & (df.cancer_type != "BORST LONG")
    )

    if group == "healthy":
        df_group = df[healthy_mask]
    elif group == "unhealthy":
        df_group = df[~healthy_mask]
        df_group = df_group.dropna(subset=["sex"])
    elif group == "all":
        df_group = df
        df_group = df_group.dropna(subset=["sex"])
    else:
        raise ValueError("Invalid group name: " + group)

    return df_group


def normalise_bps(df: pd.DataFrame, bps: list, norm_to: str = "height") -> pd.DataFrame:
    """
    Normalizes the base pairs (bps) data in a pandas dataframe (df) with respect to a specified column (norm_to).
    Parameters
    ----------
    df : pandas.DataFrame
        A pandas dataframe containing the base pairs data.
    bps : list
        A list of column names in the dataframe to be normalized.
    norm_to : str, optional
        The name of the column to normalize the bps data to. Default is "height".

    Returns
    -------
    pandas.DataFrame
        A new pandas dataframe with the normalized bps data.
    """
    # Calculate the normalization factor
    norm_factor = df[norm_to]

    # Normalize the bps data
    for bp in bps:
        df[bp] = df[bp] / norm_factor

    return df


def prettify_names(name: str) -> str:
    """
    This function takes a str of names as input and returns a new str with the names prettified.
    Each name in the input str is modified by removing 'bp_' prefix and capitalizing the first letter of the name.

    :param name: A name str to be prettified.
    :type name: str

    :return: A prettified name.
    :rtype: str

    :raises TypeError: If the input parameter is not a str.
    """
    try:
        if not isinstance(name, str):
            raise TypeError("Input parameter must be a str.")

        return name.replace("bp_", "").replace("_", " ").title()

    except TypeError as error:
        print(error)


import pandas as pd


def min_max_scale(data: pd.DataFrame, params: list) -> pd.DataFrame:
    """
    Min-max normalization is a commonly used method to normalize data. It scales the data between the range of 0 and 1
    by subtracting the minimum value of the feature and dividing by the range of the feature (maximum value - minimum value).

    Parameters:
    data (pd.DataFrame): The input data that needs to be normalized.
    params (list): The list of feature columns which needs to be normalized.

    Returns:
    pd.DataFrame: The normalized input data with the same dimensions as the input data.

    Raises:
    TypeError: If any of the input parameters' data types are not as expected.
    ValueError: If there are any invalid values in the input data.

    Example usage:
    data = pd.read_csv('data.csv')
    params = ['age', 'income']
    normalized_data = min_max_scale(data, params)
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Data must be a pandas dataframe")
    if not isinstance(params, list):
        raise TypeError("Params must be a list of feature columns")
    for param in params:
        if param not in data.columns:
            raise ValueError("Invalid parameter name: " + param)
    for param in params:
        data[param] = (data[param] - data[param].min()) / (
            data[param].max() - data[param].min()
        )
    return data
