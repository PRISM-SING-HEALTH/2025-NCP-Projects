import streamlit as st
import pandas as pd
import os
import yaml
from export import export_to_excel
from dataframe import standardise_dataframe
from config import load_config
from validator import validate_variants


def main():
    st.title("Variant Manager")
    st.sidebar.title("Navigation")

    # Sidebar navigation
    menu = st.sidebar.radio(
        "Go to",
        ["Home", "Load Configuration", "Import Data", "Query Data", "Export Data", "Validate Variants"]
    )

    # Initialise session state for data
    if "config" not in st.session_state:
        st.session_state.config = None
    if "dataframes" not in st.session_state:
        st.session_state.dataframes = {}
    if "combined_df" not in st.session_state:
        st.session_state.combined_df = None
    if "query_result" not in st.session_state:
        st.session_state.query_result = None

    # Home Page
    if menu == "Home":
        st.write(
            """
            Welcome to the Variant Manager Application!  
            Use the navigation menu on the left to get started.
            """
        )

    # Load Configuration
    elif menu == "Load Configuration":
        st.header("Load Configuration")
        config_file = st.file_uploader("Upload Configuration File (YAML)", type="yaml")

        if config_file is not None:
            try:
                st.session_state.config = yaml.safe_load(config_file)
                st.success("Configuration file loaded successfully!")
            except yaml.YAMLError as e:
                st.error(f"Failed to load configuration file: {e}")

    # Import Data
    elif menu == "Import Data":
        st.header("Import Data")
        if st.session_state.config is None:
            st.warning("Please load a configuration file first.")
        else:
            config = st.session_state.config
            base_path = config["base_path"]
            files = config["files"]

            try:
                st.write("Importing data...")
                dataframes = {
                    "Lab Cases": pd.read_excel(f"{base_path}{files['lab_cases']}", sheet_name="Sheet1", usecols="F, AF:AI, AL"),
                    "ATM Summary": pd.read_excel(f"{base_path}{files['atm_summary']}", sheet_name="SUMMARY", usecols="A:B"),
                    "Invitae Summary": pd.read_excel(f"{base_path}{files['invitae_summary']}", sheet_name="Invitae list header", usecols="E:F, M:T"),
                    "Clinical Summary": pd.read_excel(f"{base_path}{files['clinical_summary']}", sheet_name="11 Dec", usecols="D:E, K"),
                    "Research Summary": pd.read_excel(f"{base_path}{files['research_summary']}", sheet_name="Overall List", usecols="B, W:X, AF, AS:AT, AV:AW")
                }
                st.session_state.dataframes = dataframes
                st.success("Data imported successfully!")
                st.write("Preview of imported data:")
                for name, df in dataframes.items():
                    st.write(f"### {name}")
                    st.dataframe(df.head())
            except Exception as e:
                st.error(f"Error importing data: {e}")

    # Query Data
    elif menu == "Query Data":
        st.header("Query Data")
        if not st.session_state.dataframes:
            st.warning("Please import data first.")
        else:
            if st.session_state.combined_df is None:
                st.warning("Please standardize and combine data first (go to 'Export Data').")
            else:
                combined_df = st.session_state.combined_df
                st.write("### Combined Dataframe")
                st.dataframe(combined_df)

                category = st.selectbox("Select a column to query", combined_df.columns)
                search_text = st.text_input("Enter text to search for")

                if st.button("Search"):
                    try:
                        query_result = combined_df[combined_df[category].astype(str).str.contains(search_text, case=False, na=False)]
                        if query_result.empty:
                            st.warning(f"No results found for '{search_text}' in '{category}'.")
                        else:
                            st.session_state.query_result = query_result
                            st.success(f"Found {len(query_result)} results.")
                            st.dataframe(query_result)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

    # Export Data
    elif menu == "Export Data":
        st.header("Export Data")
        if not st.session_state.dataframes:
            st.warning("Please import data first.")
        else:
            if st.button("Standardize and Combine Data"):
                try:
                    config = st.session_state.config
                    standard_columns = [
                        "MRN", "Patient Name", "Phenotype", "Solved Status",
                        "Gene", "Transcript", "Variant", "HGVSg", "HGVSc", "HGVSp"
                    ]
                    dataframes = st.session_state.dataframes
                    combined_df = pd.concat([
                        standardise_dataframe(df, standard_columns) for df in dataframes.values()
                    ], ignore_index=True)
                    st.session_state.combined_df = combined_df
                    st.success("Data standardized and combined successfully!")
                    st.dataframe(combined_df)
                except Exception as e:
                    st.error(f"Error combining data: {e}")

            if st.session_state.query_result is not None:
                st.write("### Export Query Results")
                file_name = st.text_input("Enter the output file name (without extension)")
                if st.button("Export"):
                    try:
                        output_path = f"{file_name}.xlsx"
                        export_to_excel(st.session_state.query_result, output_path)
                        st.success(f"Query results exported to {output_path}.")
                    except Exception as e:
                        st.error(f"Error exporting data: {e}")

    # Validate Variants
    elif menu == "Validate Variants":
        st.header("Validate Variants")
        if st.session_state.query_result is None:
            st.warning("Please perform a query first.")
        else:
            output_file = st.text_input("Enter the output file name for validation (without extension)")
            if st.button("Validate"):
                try:
                    validation_output = f"{output_file}_validated.xlsx"
                    validate_variants(st.session_state.query_result, validation_output)
                    st.success(f"Variants validated and saved to {validation_output}.")
                except Exception as e:
                    st.error(f"Error validating variants: {e}")


if __name__ == "__main__":
    main()
