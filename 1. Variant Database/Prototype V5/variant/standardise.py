from variant.dataframe import *



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
        A standardised DataFrame for Lab Cases.
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
    remove_duplicate_hpo_terms(std_lab_cases_df)
    std_lab_cases_df = filter_invalid_variants(std_lab_cases_df)

    return std_lab_cases_df



def standardise_invitae_summary(dataframes, standard_columns):
    """
    Standardises the Invitae Summary dataset.

    Parameters:
    -----------
    dataframes : dict
        Dictionary containing all loaded DataFrames.
    standard_columns : list
        List of standard column names to retain.

    Returns:
    --------
    pd.DataFrame
        A standardised Invitae Summary DataFrame.
    """
    invitae_summary_cols = {
        'Patient ID (MRN)': 'MRN',
        'Patient Name': 'Patient Name',
        'Result': 'Solved Status',
        'Gene': 'Gene',
        'Transcript': 'Transcript',
        'Variant': 'Variant (HGVSc)',
        'Protein Change': 'HGVSp',
    }

    standard_dataframe = standardise_dataframe(dataframes["Invitae Summary"], invitae_summary_cols, standard_columns)
    remove_duplicate_phenotypes(standard_dataframe)
    remove_duplicate_hpo_terms(standard_dataframe)
    
    return standard_dataframe



def standardise_clinical_summary(dataframes, standard_columns):
    """
    Standardises the Clinical Summary dataset.

    Parameters:
    -----------
    dataframes : dict
        Dictionary containing all loaded DataFrames.
    standard_columns : list
        List of standard column names to retain.

    Returns:
    --------
    pd.DataFrame
        A standardised Clinical Summary DataFrame.
    """
    clinical_summary_cols = {
        'Identification No.': 'MRN',
        'Medical Prob description': 'Phenotype',
        'Patient Name': 'Patient Name'
    }

    standard_dataframe = standardise_dataframe(dataframes["Clinical Summary"], clinical_summary_cols, standard_columns)
    remove_duplicate_phenotypes(standard_dataframe)
    remove_duplicate_hpo_terms(standard_dataframe)
    
    return standard_dataframe



def standardise_research_summary(dataframes, standard_columns):
    """
    Standardises the Research Summary dataset.

    Parameters:
    -----------
    dataframes : dict
        Dictionary containing all loaded DataFrames.
    standard_columns : list
        List of standard column names to retain.

    Returns:
    --------
    pd.DataFrame
        A standardised Research Summary DataFrame.
    """
    standard_dataframe = standardise_and_transform_research(dataframes["Research Summary"])
    standard_dataframe = standard_dataframe.loc[:, standard_dataframe.columns.intersection(standard_columns)]
    standard_dataframe = standard_dataframe.reindex(columns=standard_columns)
    remove_duplicate_phenotypes(standard_dataframe)
    remove_duplicate_hpo_terms(standard_dataframe)
    
    return standard_dataframe



def standardise_atm_summary(dataframes, standard_columns):
    """
    Standardises the ATM Summary dataset.

    Parameters:
    -----------
    dataframes : dict
        Dictionary containing all loaded DataFrames.
    standard_columns : list
        List of standard column names to retain.

    Returns:
    --------
    pd.DataFrame
        A standardised ATM Summary DataFrame.
    """
    standard_dataframe = standardise_and_transform_atm(dataframes["ATM Summary"])
    standard_dataframe = standard_dataframe.loc[:, standard_dataframe.columns.intersection(standard_columns)]
    standard_dataframe = standard_dataframe.reindex(columns=standard_columns)
    remove_duplicate_phenotypes(standard_dataframe)
    remove_duplicate_hpo_terms(standard_dataframe)
    
    return standard_dataframe



def standardise_other_datasets(dataframes, standard_columns):
    """
    Stores standardised dataframes into a dictionary.

    Parameters:
    -----------
    dataframes : dict
        Dictionary containing all loaded DataFrames.
    standard_columns : list
        List of standard column names to retain.

    Returns:
    --------
    dict
        A dictionary of standardised DataFrames.
    """

    standard_dataframes_dict = {
        "Invitae Summary": standardise_invitae_summary(dataframes, standard_columns),
        "Clinical Summary": standardise_clinical_summary(dataframes, standard_columns),
        "Research Summary": standardise_research_summary(dataframes, standard_columns),
        "ATM Summary": standardise_atm_summary(dataframes, standard_columns)
    }

    return standard_dataframes_dict



def combine_standardised_data(std_dataframes):
    """
    Combines all standardised DataFrames into a single DataFrame.

    Parameters:
    -----------
    std_dataframes : dict
        Dictionary containing the standardised DataFrames.

    Returns:
    --------
    pd.DataFrame
        A combined DataFrame of all standardised datasets.
    """
    combined_df = pd.concat(
        [
            std_dataframes["Lab Cases"],
            std_dataframes["Invitae Summary"],
            std_dataframes["Clinical Summary"],
            std_dataframes["Research Summary"],
            std_dataframes["ATM Summary"]
        ],
        axis=0, ignore_index=True
    )
    # Convert float columns to integers
    numeric_columns = ["Var Number", "Var Count"]  # Add other numeric columns if needed
    combined_df[numeric_columns] = combined_df[numeric_columns].round(0).astype("Int64")  # Int64 allows NaN values
    
    return combined_df



def standardise_data(dataframes, standard_columns):
    """
    Standardises all datasets and combines them into a single DataFrame.

    Parameters:
    -----------
    dataframes : dict
        Dictionary containing all loaded DataFrames.
    standard_columns : list
        List of standard column names to retain.

    Returns:
    --------
    pd.DataFrame
        A combined DataFrame with all datasets standardised.
    """
    std_lab_cases_df = standardise_lab_cases(dataframes, standard_columns)
    std_other_datasets = standardise_other_datasets(dataframes, standard_columns)

    # Merge the lab cases DataFrame with the other standardised datasets
    std_other_datasets["Lab Cases"] = std_lab_cases_df

    new_df = combine_standardised_data(std_other_datasets)

    return new_df



def generate_hgvs_column(df):
    """
    Generates an HGVS-formatted column by combining 'Transcript' and 'Variant (HGVSc)'.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing variant data.

    Returns:
    --------
    pd.DataFrame
        The DataFrame with an additional 'HGVS (HGVSc)' column.
    """
    df['HGVS (HGVSc)'] = df['Transcript'] + ":" + df['Variant (HGVSc)']
    
    return df
