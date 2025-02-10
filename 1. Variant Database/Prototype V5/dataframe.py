import re
import pandas as pd
import streamlit as st

def convert_dataframes_to_string(dataframes):
    """
    Converts all values in the given DataFrames to strings.

    Parameters:
    -----------
    dataframes : dict
        A dictionary of pandas DataFrames.

    Returns:
    --------
    dict
        A dictionary of pandas DataFrames with all values as strings.
    """
    if dataframes:
        return {key: df.astype(str) for key, df in dataframes.items()}
    return None

def standardise_lab_cases(dataframes, standard_columns):
    """
    Standardises the Lab Cases dataset.

    Parameters:
    -----------
    dataframes : dict
        Dictionary containing all loaded DataFrames.
    standard_columns : list
        List of standard column names to retain.

    Returns:
    --------
    pd.DataFrame
        A standardized DataFrame for Lab Cases.
    """
    lab_cases_cols = {
        'G4K Sample ID': 'MRN',
        'Number variants detected': 'Var Count',
        'Variant_Number': 'Var Number',
        'gene': 'Gene',
        'type': 'Type',
        'zygosity': 'Zygosity',
        'inheritance': 'Inheritance'
    }

    std_lab_cases_df = standardise_and_transform_lab_cases(dataframes["Lab Cases"])
    std_lab_cases_df.rename(columns=lab_cases_cols, inplace=True)
    std_lab_cases_df = std_lab_cases_df.loc[:, std_lab_cases_df.columns.intersection(standard_columns)]
    std_lab_cases_df = std_lab_cases_df.reindex(columns=standard_columns)
    remove_duplicate_phenotypes(std_lab_cases_df)
    std_lab_cases_df = filter_invalid_variants(std_lab_cases_df)

    return std_lab_cases_df











def standardise_dataframe(df, column_mapping, standard_columns):
    """
    Standardises a Dataframe by renaming columns, retaining only specified standard columns, 
    and reordering them in the given order.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input Dataframe to be standardised.
    column_mapping : dict
        A dictionary mapping existing column names to their standardised names.
    standard_columns : list
        A list of column names that should be retained and ordered in the final Dataframe.

    Returns:
    --------
    pandas.DataFrame
        A standardised Dataframe with renamed, filtered, and ordered columns.
    """
    # Rename columns
    df.rename(columns=column_mapping, inplace=True)

    # Filter to retain only standard columns
    std_df = df.loc[:, df.columns.intersection(standard_columns)]

    # Ensure columns are in the exact order of standard columns
    std_df = std_df.reindex(columns=standard_columns)

    return std_df




def remove_duplicate_phenotypes(df):
    """
    Removes duplicate phenotype entries for the same MRN.
    
    If multiple rows share the same MRN, only the first occurrence retains its 
    phenotype description, while subsequent duplicates have their phenotype set to an 
    empty string.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame containing 'MRN' and 'Phenotype' columns.

    Returns:
    --------
    None
        The function modifies the DataFrame in place.

    Notes:
    ------
    - Assumes 'MRN' and 'Phenotype' columns are present in the DataFrame.
    - If either column is missing, a warning message is displayed using Streamlit.
    """
    if 'MRN' in df.columns and 'Phenotype' in df.columns:
        df.loc[df.duplicated(subset=['MRN'], keep='first'), 'Phenotype'] = ""
    else:
        st.warning("The 'MRN' or 'Phenotype' column is missing in the dataframe.")




def filter_invalid_variants(df):
    """
    Filters out rows where the 'Var Number' exceeds the 'Var Count'.

    This function ensures that both 'Var Number' and 'Var Count' columns are 
    numeric and removes any rows where 'Var Number' is greater than 'Var Count'.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame containing 'Var Number' and 'Var Count' columns.

    Returns:
    --------
    pandas.DataFrame
        A filtered DataFrame where all rows have 'Var Number' less than or 
        equal to 'Var Count'.

    Notes:
    ------
    - Converts 'Var Number' and 'Var Count' to numeric, coercing errors to NaN.
    - Any non-numeric values in these columns will be converted to NaN.
    - Rows with NaN values in 'Var Number' or 'Var Count' are retained 
      unless they violate the filtering condition.
    """
    if 'Var Count' in df.columns and 'Var Number' in df.columns:
        # Ensure 'Var Count' and 'Var Number' are numeric
        df['Var Count'] = pd.to_numeric(df['Var Count'], errors='coerce')
        df['Var Number'] = pd.to_numeric(df['Var Number'], errors='coerce')

        # Filter out rows where 'Var Number' > 'Var Count'
        df = df[df['Var Number'] <= df['Var Count']]

    return df




def standardise_and_transform_lab_cases(df):
    """
    Standardises variant related columns in Lab Case data and reshapes the DataFrame 
    so that variants are displayed vertically.

    This function:
    1. Identifies all variant related columns dynamically.
    2. Renames variant columns into a standardised format.
    3. Transforms the DataFrame from wide format to long format, 
       displaying variant related data as separate rows.
    4. Extracts and separates the variant number and field type.
    5. Pivots the DataFrame to organise fields as columns.
    6. Separates the 'HGVSc' column into 'Transcript' and 'Variant (HGVSc)' if present.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame containing lab case variant data with columns formatted as 'Variant_X_FieldName'.

    Returns:
    --------
    pandas.DataFrame
        A transformed DataFrame where each variant is represented as a row, 
        with variant attributes organised as columns.
    """
    # Identify all variant related columns dynamically
    variant_cols = [col for col in df.columns if re.match(r'Variant_\d+_.*', col)]

    # Create a mapping of columns for standardisation
    column_mapping = {}
    for col in variant_cols:
        # Extract the variant number and field name safely
        variant_num_match = re.search(r'Variant_(\d+)_', col)
        if variant_num_match:  # Only proceed if the pattern matches
            variant_num = variant_num_match.group(1)
            field_name = col.split('_', 2)[2]  # Extract field name (e.g., gene, HGVSg, etc.)
            column_mapping[col] = f"{field_name}_{variant_num}"  # Standardise the column name

    # Rename the columns
    df.rename(columns=column_mapping, inplace=True)

    # Reshape the dataframe: Convert variant columns to rows
    variant_cols = [col for col in df.columns if re.match(r'.*_\d+', col)]  # Dynamically find all variant columns
    id_vars = [col for col in df.columns if col not in variant_cols]  # Non-variant columns as identifiers

    # Melt the dataframe to long format
    df_long = df.melt(id_vars=id_vars, var_name='Variant_Field', value_name='Value')

    # Extract variant number and field type from the melted "Variant_Field"
    df_long['Variant_Number'] = df_long['Variant_Field'].apply(
        lambda x: re.search(r'_(\d+)$', x).group(1) if re.search(r'_(\d+)$', x) else None
    )
    df_long['Field'] = df_long['Variant_Field'].apply(
        lambda x: re.sub(r'_(\d+)$', '', x) if re.search(r'_(\d+)$', x) else None
    )

    # Drop rows with invalid "Variant_Field"
    df_long.dropna(subset=['Variant_Number', 'Field'], inplace=True)

    # Pivot the dataframe to make "Field" the columns
    df_pivot = df_long.pivot(index=id_vars + ['Variant_Number'], columns='Field', values='Value').reset_index()

    # Separate HGVSc into Transcript and Variant columns
    if 'HGVSc' in df_pivot.columns:
        df_pivot[['Transcript', 'Variant (HGVSc)']] = df_pivot['HGVSc'].str.split(':', expand=True)
        df_pivot.drop(columns=['HGVSc'], inplace=True)  # Drop the original combined column

    return df_pivot




def standardise_and_transform_research(df):
    """
    Standardises Research Summary columns and reshapes the DataFrame so that 
    variants are displayed vertically, dynamically handling multiple candidate genes.

    This function:
    1. Renames specific columns using a predefined mapping.
    2. Dynamically detects variant-related columns (e.g., Candidate Gene, Transcript, cDNA, etc.).
    3. Reshapes the DataFrame by creating separate rows for each variant associated with a patient.
    4. Assigns a sequential "Var Number" to each variant per patient.
    5. Adds a "Var Count" column to indicate the total number of variants per patient.
    6. Ensures only the first occurrence of "Phenotype" is retained per patient.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame containing research summary data with variant-related columns.

    Returns:
    --------
    pandas.DataFrame
        A transformed DataFrame where each variant is represented as a row, 
        with attributes like Gene, Transcript, HGVSc, HGVSp, Zygosity, and Variant Type 
        organised into separate columns.

    Notes:
    ------
    - The function detects variant-related columns dynamically.
    - The reshaped DataFrame ensures each variant appears as a separate row.
    - "Var Number" is assigned sequentially for each patient.
    - "Var Count" tracks the number of variants associated with each patient.
    - If 'MRN' or 'Phenotype' is missing, a warning is displayed using Streamlit.
    """
    # Standardise column names with a predefined mapping
    column_mapping = {
        'IC No (MRN)': 'MRN',
        'Name': 'Patient Name',
        'AUTO STATUS': 'Solved Status',
        'Phenotype Description': 'Phenotype'
    }

    # Rename static columns
    df.rename(columns=column_mapping, inplace=True)

    # Dynamically identify all candidate gene-related columns
    variant_columns = [col for col in df.columns if col.startswith('Candidate gene')]
    transcript_columns = [col for col in df.columns if col.startswith('Transcript')]
    cdna_columns = [col for col in df.columns if col.startswith('cDNA')]
    protein_columns = [col for col in df.columns if col.startswith('Protein')]
    zygosity_columns = [col for col in df.columns if col.startswith('Zygosity')]
    variant_type_columns = [col for col in df.columns if col.startswith('Variant Type')]

    # Collect all dynamically identified columns
    dynamic_columns = {
        'Gene': variant_columns,
        'Transcript': transcript_columns,
        'Variant (HGVSc)': cdna_columns,
        'HGVSp': protein_columns,
        'Zygosity': zygosity_columns,
        'Variant Type': variant_type_columns
    }

    # Reshape the DataFrame
    rows = []  # To store reshaped rows
    for _, row in df.iterrows():
        for i in range(len(variant_columns)):  # Iterate over the number of variant columns
            # Extract data for the i-th variant
            variant_data = {
                'MRN': row['MRN'],
                'Patient Name': row['Patient Name'],
                'Solved Status': row['Solved Status'],
                'Phenotype': row['Phenotype'],
                'Var Number': i + 1,  # Dynamically assign variant number
                'Gene': row[variant_columns[i]] if i < len(variant_columns) else None,
                'Transcript': row[transcript_columns[i]] if i < len(transcript_columns) else None,
                'Variant (HGVSc)': row[cdna_columns[i]] if i < len(cdna_columns) else None,
                'HGVSp': row[protein_columns[i]] if i < len(protein_columns) else None,
                'Zygosity': row[zygosity_columns[i]] if i < len(zygosity_columns) else None,
                'Variant Type': row[variant_type_columns[i]] if i < len(variant_type_columns) else None
            }
            rows.append(variant_data)

    # Create a new DataFrame from the reshaped rows
    reshaped_df = pd.DataFrame(rows)

    # Add a 'Var Count' column dynamically based on the number of variants per MRN
    reshaped_df['Var Count'] = reshaped_df.groupby('MRN')['Var Number'].transform('max')

    # Remove duplicate Phenotype entries for each patient.
    if 'MRN' in reshaped_df and 'Phenotype' in reshaped_df.columns:
        reshaped_df.loc[reshaped_df.duplicated(subset=['MRN'], keep='first'), 'Phenotype'] = ""
    else:
        st.warning("The 'MRN' or 'Phenotype' column is missing in the dataframe.")

    return reshaped_df




def standardise_and_transform_atm(df):
    """
    Standardise ATM summary columns and reshape the dataframe for consistent formatting.
    """

    # Standardise column names with a predefined mapping
    column_mapping = {
        'HGVS_Genomic_GRCh38/hg38': 'HGVSg',
        'HGVS_MANE Select_Transcript_RefSeq': 'Transcript',
        'HGVS_MANE Select_cDNA': 'Variant (HGVSc)',
        'HGVS_MANE Select_protein': 'HGVSp',
        'HUGO gene symbol': 'Gene',
    }

    # Rename columns
    df.rename(columns=column_mapping, inplace=True)

    # Define standard columns
    standard_columns = [
        'Gene', 'Transcript', 'HGVSg', 'Variant (HGVSc)', 'HGVSp'
    ]

    # Filter to retain only standard columns
    std_df = df.loc[:, df.columns.intersection(standard_columns)]

    # Ensure columns are in the exact order of standard columns
    std_df = std_df.reindex(columns=standard_columns)

    return std_df



def standardise_and_transform_atm(df):
    """
    Standardises ATM summary columns and reshapes the DataFrame for consistent formatting.

    This function:
    1. Renames specific columns based on a predefined mapping.
    2. Retains only the essential standard columns relevant to ATM data.
    3. Ensures that the columns are presented in a consistent and expected order.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame containing ATM summary data with various column naming conventions.

    Returns:
    --------
    pandas.DataFrame
        A standardised DataFrame containing only the relevant columns in the correct order.

    Notes:
    ------
    - Columns are renamed to a consistent format to match standard conventions.
    - Only the columns ['Gene', 'Transcript', 'HGVSg', 'Variant (HGVSc)', 'HGVSp'] are retained.
    - If any of the expected columns are missing, they will appear as NaN in the final DataFrame.
    """
    # Standardise column names with a predefined mapping
    column_mapping = {
        'HGVS_Genomic_GRCh38/hg38': 'HGVSg',
        'HGVS_MANE Select_Transcript_RefSeq': 'Transcript',
        'HGVS_MANE Select_cDNA': 'Variant (HGVSc)',
        'HGVS_MANE Select_protein': 'HGVSp',
        'HUGO gene symbol': 'Gene',
    }

    # Rename columns
    df.rename(columns=column_mapping, inplace=True)

    # Define standard columns
    standard_columns = [
        'Gene', 'Transcript', 'HGVSg', 'Variant (HGVSc)', 'HGVSp'
    ]

    # Filter to retain only standard columns
    std_df = df.loc[:, df.columns.intersection(standard_columns)]

    # Ensure columns are in the exact order of standard columns
    std_df = std_df.reindex(columns=standard_columns)

    return std_df
