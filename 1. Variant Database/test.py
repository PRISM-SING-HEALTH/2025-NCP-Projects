import streamlit as st
import pandas as pd
import yaml
from dataframe import *
from query import *
from validator import *


# Initialising Streamlit App Interface
st.title("Genetic Variant Database Manager")
st.sidebar.title("Navigation")

# YAML Configuration Selection
yaml_file = st.sidebar.file_uploader("Upload YAML Configuration File", type=["yaml", "yml"])
if yaml_file:
    try:
        # Parse the uploaded YAML file
        config = yaml.safe_load(yaml_file)
        base_path = config['base_path']
        local_path = config['local_path']
        files = config['files']
        st.sidebar.success("YAML configuration loaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Failed to load YAML configuration: {e}")
        config = None
else:
    st.sidebar.warning("Please upload a YAML configuration file.")
    config = None

# Navigation
options = ["No Option Selected","Load Data", "Query Data", "Validate Variants"]
choice = st.sidebar.selectbox("Select Action", options)

# Global variable to store loaded Dataframes
dataframes = {}

if config:
    standard_columns = [
        'MRN',
        'Patient Name',
        'Var Count',
        'Var Number',
        'Phenotype',
        'Solved Status',
        'Gene',
        'HGVSg',
        'Transcript',
        'Variant (HGVSc)',
        'HGVSp',
        'Type',
        'Zygosity',
        'Inheritance',
    ]

    # Stores renamed column names from each dataframe
    renaming_maps = {}

    # Option 1: Load Excel Data
    if choice == "Load Data":
        st.header("Load Excel Data")

        try:
            # Load and read individual dataframes
            st.write("Loading data...")

            # Reading files in conventional format
            lab_cases_df = pd.read_excel(f"{base_path}{files['lab_cases']}", sheet_name='Sheet1', header=0)
            invitae_summary_df = pd.read_excel(f"{base_path}{files['invitae_summary']}", sheet_name='Invitae list header', header=0)
            clinical_summary_df = pd.read_excel(f"{base_path}{files['clinical_summary']}", sheet_name='11 Dec', header=0)
            research_summary_df = pd.read_excel(f"{base_path}{files['research_summary']}", sheet_name='Overall List', header=2)

            # Reading unconventional format
            atm_summary_df = pd.read_excel(f"{base_path}{files['atm_summary']}", sheet_name='SUMMARY', header=None)

            # Additional filtering due to unconventional formatting
            atm_summary_df_filtered = atm_summary_df.iloc[8:17]  # Ensure rows are correctly indexed
            atm_summary_df_filtered.reset_index(drop=True, inplace=True)  # Reset index for clean output

            # Convert to a structured DataFrame
            atm_structured_df = atm_summary_df_filtered.set_index(0).T  # Set column 0 as the header, transpose
            atm_structured_df.reset_index(drop=True, inplace=True)  # Reset index for clean final DataFrame

            # Store imported dataframes into a dictionary
            dataframes = {
                "Lab Cases": lab_cases_df,
                "ATM Summary": atm_structured_df,
                "Invitae Summary": invitae_summary_df,
                "Clinical Summary": clinical_summary_df,
                "Research Summary": research_summary_df,
            }

            st.success("Data successfully loaded!")

        except FileNotFoundError as e:
            st.error(f"File not found: {e}")
        except ValueError as e:
            st.error(f"Error reading sheet or invalid data format: {e}")

        # Displaying loaded dataframes
        st.write("### Loaded Dataframes:")
        for name, df in dataframes.items():
            st.write(f"#### {name}", df.head())

        # Button to Standardise Data
        if st.button("Standardise Data"):
            try:
                # Standardising Lab Cases Layout
                lab_cases_cols = {
                    'G4K Sample ID': 'MRN',  # Using G4K ID as MRN as a placeholder.
                    'Number variants detected': 'Var Count',
                    'Variant_Number': 'Var Number',
                    'gene': 'Gene',
                    'type': 'Type',
                    'zygosity': 'Zygosity',
                    'inheritance': 'Inheritance'
                }

                std_lab_cases_df = standardise_and_transform_lab_cases(lab_cases_df)
                std_lab_cases_df.rename(columns=lab_cases_cols, inplace=True)
                std_lab_cases_df = std_lab_cases_df.loc[:, std_lab_cases_df.columns.intersection(standard_columns)]
                std_lab_cases_df = std_lab_cases_df.reindex(columns=standard_columns)
                remove_duplicate_phenotypes(std_lab_cases_df)
                std_lab_cases_df = filter_invalid_variants(std_lab_cases_df)

                # Standardising Invitae Layout
                invitae_summary_df_cols = {
                    'Patient ID (MRN)': 'MRN',
                    'Patient Name': 'Patient Name',
                    'Result': 'Solved Status',
                    'Gene': 'Gene',
                    'Transcript': 'Transcript',
                    'Variant': 'Variant (HGVSc)',
                    'Protein Change': 'HGVSp',
                }

                std_invitae_summary_df = standardise_dataframe(invitae_summary_df, invitae_summary_df_cols, standard_columns)

                # Standardising Clinical Summary
                clinical_summary_df_cols = {
                    'Identification No.': 'MRN',
                    'Medical Prob description': 'Phenotype',
                    'Patient Name': 'Patient Name'
                }

                std_clinical_summary_df = standardise_dataframe(clinical_summary_df, clinical_summary_df_cols, standard_columns)

                # Standardising Research Summary
                std_research_summary_df = standardise_and_transform_research(research_summary_df)
                std_research_summary_df = std_research_summary_df.loc[:, std_research_summary_df.columns.intersection(standard_columns)]
                std_research_summary_df = std_research_summary_df.reindex(columns=standard_columns)

                # Standardising ATM Summary
                std_atm_summary_df = standardise_and_transform_atm(atm_structured_df)
                std_atm_summary_df = std_atm_summary_df.loc[:, std_atm_summary_df.columns.intersection(standard_columns)]
                std_atm_summary_df = std_atm_summary_df.reindex(columns=standard_columns)

                # Displaying standardised dataframes
                st.success("Data successfully standardised!")

                st.write(f"### Standardised Lab Cases")
                st.write(std_lab_cases_df)

                st.write(f"### Standardised Invitae Cases")
                st.write(std_invitae_summary_df)

                st.write(f"### Standardised Clinical Cases")
                st.write(std_clinical_summary_df)

                st.write(f"### Standardised Research Cases")
                st.write(std_research_summary_df)

                st.write(f"### Standardised ATM Cases")
                st.write(std_atm_summary_df)

                # Combine all standardised dataframes
                combined_df = pd.concat(
                    [
                        std_lab_cases_df,
                        std_invitae_summary_df,
                        std_clinical_summary_df,
                        std_research_summary_df,
                        std_atm_summary_df
                    ],
                    axis=0,
                    ignore_index=True
                )

                # Store the combined dataframe in session state
                st.session_state['Combined'] = combined_df

                st.success("Data successfully standardised and combined!")

                st.write("### Combined Dataframe")
                st.write(combined_df)

            except Exception as e:
                st.error(f"Failed to standardise data: {e}")



    # Option 2: Query
    elif choice == "Query Data":
        if 'Combined' in st.session_state:
            combined_df = st.session_state['Combined']
            query(combined_df)
        else:
            st.warning("Please standardise and combine dataframes before querying.")


                   

    elif choice == "Validate Variants":
        st.title("Batch Variant Validator")
    
        # File uploader for user to upload a CSV file containing variants
        uploaded_file = st.file_uploader("Upload CSV file with variants", type=["csv"])
    
        if uploaded_file:
            # Load the CSV file into a DataFrame
            df = pd.read_csv(uploaded_file)
    
            # Ensure the required columns exist
            if 'Transcript' not in df.columns or 'Variant (HGVSc)' not in df.columns:
                st.error("Uploaded file must contain both 'Transcript' and 'Variant (HGVSc)' columns.")
            else:
                st.success("File uploaded successfully!")
                st.write("### Uploaded Variants")
                st.dataframe(df)
    
                # Combine Transcript and Variant columns to create HGVS-compatible format
                df['HGVS (HGVSc)'] = df['Transcript'] + ":" + df['Variant (HGVSc)']
    
                # Validate the variants when the user clicks the button
                if st.button("Validate Variants"):
                    with st.spinner("Validating variants..."):
                        variants_list = df['HGVS (HGVSc)'].tolist()
                        results_df = test_variant_validator_batch(variants_list)
    
                    # Display the validation results
                    st.success("Validation completed!")
                    st.write("### Validation Results")
                    st.dataframe(results_df)
    
                    # Provide a download button for the results
                    csv_data = results_df.to_csv(index=False)
                    st.download_button(
                        label="Download Validation Results as CSV",
                        data=csv_data,
                        file_name="validation_results.csv",
                        mime="text/csv",
                    )

