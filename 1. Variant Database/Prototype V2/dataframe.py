import numpy as np

def standardise_dataframe(df, columns):
  """
  Converts unstandardised dataframe to standardised dataframe.

  Args:
    df (pd.DataFrame): Input dataframe.
    columns (list): List of standardised column names.

  Returns:
    standardised_df (pd.DataFrame): Standardized dataframe.
  """
  standardised_df = df.reindex(columns = columns, fill_value = np.nan)
  return standardised_df
