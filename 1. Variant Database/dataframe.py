import re
import pandas as pd
import streamlit as st



def standardise_dataframe(df, column_mapping, standard_columns):
    """
    Standardises a DataFrame by renaming columns, retaining only standard columns, 
    and reordering them in the specified order.
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
    Removes duplicate Phenotype entries for the same MRN.
    """
    if 'MRN' in df.columns and 'Phenotype' in df.columns:
        df.loc[df.duplicated(subset=['MRN'], keep='first'), 'Phenotype'] = ""
    else:
        st.warning("The 'MRN' or 'Phenotype' column is missing in the dataframe.")



def filter_invalid_variants(df):
    """
    Removes rows where Var Number exceeds Var Count.
    """
    if 'Var Count' in df.columns and 'Var Number' in df.columns:
        # Ensure Var Count and Var Number are numeric
        df['Var Count'] = pd.to_numeric(df['Var Count'], errors='coerce')
        df['Var Number'] = pd.to_numeric(df['Var Number'], errors='coerce')

        # Filter out rows where Var Number > Var Count
        df = df[df['Var Number'] <= df['Var Count']]

    return df



def standardise_and_transform_lab_cases(df):
    """
    Standardise lab cases variant columns and reshape the dataframe so variants are displayed vertically.
    """

    # Identify all variant-related columns dynamically
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
    Standardise research summary columns and reshape the dataframe 
    so that variants are displayed vertically, dynamically handling multiple candidate genes.
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

    # Dynamically identify all candidate gene-related columns (e.g., Candidate gene (1), (2), ...)
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

    # Remove duplicate Phenotype entires for each patient.
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
