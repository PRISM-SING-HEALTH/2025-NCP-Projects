import streamlit as st
import pandas as pd
import requests

# ---------------
# HELPER FUNCTIONS
# ---------------

import pandas as pd
import requests

def validate_base_gene(base_csv_path):
    """
    Reads all rows from a CSV with a 'Gene' column, queries the VariantValidator API for each gene,
    and returns a DataFrame with columns: ['Gene', 'Reference', 'Message'].

    NOTE: We now store the top-level gene symbol (e.g. 'CDK13') in 'Reference',
    instead of storing the transcript accession (e.g. 'NM_003718.5').
    """

    results = []

    try:
        df = pd.read_csv(base_csv_path)
        if "Gene" not in df.columns:
            return pd.DataFrame([{
                "Gene": None,
                "Reference": None,
                "Message": "Error: CSV file must contain a 'Gene' column."
            }])

        if df.empty:
            return pd.DataFrame([{
                "Gene": None,
                "Reference": None,
                "Message": "Error: CSV file is empty, cannot validate base gene."
            }])

        # Iterate through each row's gene
        for idx, row in df.iterrows():
            gene_query = row["Gene"]

            # Construct the API URL
            url = (
                f"https://rest.variantvalidator.org/VariantValidator/tools/gene2transcripts_v2/"
                f"{gene_query}/mane_select/refseq/GRCh38?content-type=application%2Fjson"
            )
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    results.append({
                        "Gene": gene_query,
                        "Reference": None,
                        "Message": f"Error: API call failed with status code {response.status_code}."
                    })
                    continue

                # The response is typically a list with one item
                data = response.json()
                if not isinstance(data, list) or len(data) == 0:
                    results.append({
                        "Gene": gene_query,
                        "Reference": None,
                        "Message": "Error: Response did not return a non-empty list."
                    })
                    continue

                first_record = data[0]

                # Instead of grabbing transcripts[0]["reference"], we want the top-level gene symbol
                # Usually "current_symbol" or "requested_symbol"
                gene_symbol = first_record.get("current_symbol") or first_record.get("requested_symbol")
                if not gene_symbol:
                    results.append({
                        "Gene": gene_query,
                        "Reference": None,
                        "Message": "Error: 'current_symbol' or 'requested_symbol' not found in the response."
                    })
                    continue

                # Success: we store the gene symbol in the 'Reference' column
                results.append({
                    "Gene": gene_query,
                    "Reference": gene_symbol,
                    "Message": f"Validated: Base gene '{gene_query}' => symbol '{gene_symbol}'."
                })

            except Exception as api_error:
                results.append({
                    "Gene": gene_query,
                    "Reference": None,
                    "Message": f"Error during API call: {api_error}"
                })

    except Exception as e:
        # If we fail to read the file or another top-level error occurs
        return pd.DataFrame([{
            "Gene": None,
            "Reference": None,
            "Message": f"Error during base gene validation: {e}"
        }])

    # Convert the list of dicts to a DataFrame
    return pd.DataFrame(results)



def validate_comparison_variant(comparison_csv_path):
    """
    Reads all rows from a CSV with 'Transcript' and 'Variant (HGVSc)' columns, queries the VariantValidator API,
    and returns a DataFrame with columns: ['Transcript', 'Variant (HGVSc)', 'Gene Symbol', 'Message'].
    """
    results = []

    try:
        df = pd.read_csv(comparison_csv_path)
        required_cols = {"Transcript", "Variant (HGVSc)"}
        if not required_cols.issubset(df.columns):
            # Return a one-row DataFrame indicating error
            return pd.DataFrame([{
                "Transcript": None,
                "Variant (HGVSc)": None,
                "Gene Symbol": None,
                "Message": "Error: CSV file must contain 'Transcript' and 'Variant (HGVSc)' columns."
            }])

        if df.empty:
            # Return a one-row DataFrame indicating error
            return pd.DataFrame([{
                "Transcript": None,
                "Variant (HGVSc)": None,
                "Gene Symbol": None,
                "Message": "Error: The CSV file is empty."
            }])

        # Iterate through each row
        for idx, row in df.iterrows():
            transcript = row["Transcript"]
            variant_hgvsc = row["Variant (HGVSc)"]
            variant_description = f"{transcript}:{variant_hgvsc}"

            url = (
                "https://rest.variantvalidator.org/VariantValidator/"
                f"variantvalidator/GRCh38/{variant_description}/mane_select?"
                "content-type=application%2Fjson"
            )
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    results.append({
                        "Transcript": transcript,
                        "Variant (HGVSc)": variant_hgvsc,
                        "Gene Symbol": None,
                        "Message": f"Error: API call failed with status code {response.status_code}."
                    })
                    continue

                data = response.json()
                variant_data = data.get(variant_description)
                if variant_data is None:
                    results.append({
                        "Transcript": transcript,
                        "Variant (HGVSc)": variant_hgvsc,
                        "Gene Symbol": None,
                        "Message": f"Error: '{variant_description}' key not found in API response."
                    })
                    continue

                gene_symbol = variant_data.get("gene_symbol")
                if gene_symbol is None:
                    results.append({
                        "Transcript": transcript,
                        "Variant (HGVSc)": variant_hgvsc,
                        "Gene Symbol": None,
                        "Message": "Error: 'gene_symbol' not found in the variant data."
                    })
                    continue

                # Success!
                results.append({
                    "Transcript": transcript,
                    "Variant (HGVSc)": variant_hgvsc,
                    "Gene Symbol": gene_symbol,
                    "Message": (
                        f"Validated: Comparison variant '{variant_description}' "
                        f"has gene symbol '{gene_symbol}'."
                    )
                })

            except Exception as api_error:
                results.append({
                    "Transcript": transcript,
                    "Variant (HGVSc)": variant_hgvsc,
                    "Gene Symbol": None,
                    "Message": f"Error during API call: {api_error}"
                })

    except Exception as e:
        # If we fail to read the file or some other top-level error
        return pd.DataFrame([{
            "Transcript": None,
            "Variant (HGVSc)": None,
            "Gene Symbol": None,
            "Message": f"Error during comparison variant validation: {e}"
        }])

    # Convert the list of results to a DataFrame
    return pd.DataFrame(results)



def compare_base_and_comparison(base_reference, comparison_gene_symbol):
    """
    Compares the base gene 'reference' with the comparison variant 'gene_symbol'.
    """
    if base_reference is None or comparison_gene_symbol is None:
        return "Comparison cannot be made because one or both gene values are missing."

    if str(base_reference).strip().upper() == str(comparison_gene_symbol).strip().upper():
        return (
            f"Match: Base gene '{base_reference}' matches "
            f"comparison gene symbol '{comparison_gene_symbol}'."
        )
    else:
        return (
            f"Mismatch: Base gene '{base_reference}' does NOT match "
            f"comparison gene symbol '{comparison_gene_symbol}'."
        )



def compare_all_base_and_comparison(base_df, comp_df):
    """
    Performs a row-by-row comparison between a base DataFrame (with columns ['Gene', 'Reference'])
    and a comparison DataFrame (with columns ['Transcript', 'Variant (HGVSc)', 'Gene Symbol'])
    using the existing 'compare_base_and_comparison' function.

    Returns a new DataFrame with columns:
      'Gene', 'Reference', 'Transcript', 'Variant (HGVSc)', 'Gene Symbol', 'ComparisonResult'
    """
    results = []

    # Figure out how many rows to compare (use the larger of the two DataFrames)
    max_rows = max(len(base_df), len(comp_df))

    for i in range(max_rows):
        # Safely extract from base_df if row i exists
        if i < len(base_df):
            base_gene = base_df.loc[i, "Gene"] if "Gene" in base_df.columns else None
            base_reference = base_df.loc[i, "Reference"] if "Reference" in base_df.columns else None
        else:
            base_gene = None
            base_reference = None

        # Safely extract from comp_df if row i exists
        if i < len(comp_df):
            transcript = comp_df.loc[i, "Transcript"] if "Transcript" in comp_df.columns else None
            variant_hgvsc = comp_df.loc[i, "Variant (HGVSc)"] if "Variant (HGVSc)" in comp_df.columns else None
            comp_gene_symbol = comp_df.loc[i, "Gene Symbol"] if "Gene Symbol" in comp_df.columns else None
        else:
            transcript = None
            variant_hgvsc = None
            comp_gene_symbol = None

        # Compare using your existing single-record function
        comparison_msg = compare_base_and_comparison(base_reference, comp_gene_symbol)

        # Append the results
        results.append({
            "Gene": base_gene,
            "Reference": base_reference,
            "Transcript": transcript,
            "Variant (HGVSc)": variant_hgvsc,
            "Gene Symbol": comp_gene_symbol,
            "ComparisonResult": comparison_msg
        })

    return pd.DataFrame(results)


def load_uploaded_variant_file(uploaded_file):
    """
    Loads and validates an uploaded CSV with required columns: 'Transcript', 'Variant (HGVSc)'.
    """
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"❌ Could not read the uploaded file: {e}")
        return None

    required_columns = {"Transcript", "Variant (HGVSc)"}
    if not required_columns.issubset(df.columns):
        st.error("❌ Uploaded file must contain 'Transcript' and 'Variant (HGVSc)' columns.")
        return None

    if df.empty:
        st.error("❌ Uploaded file is empty.")
        return None

    st.success("✅ File uploaded successfully!")
    return df


def generate_hgvs_column(df):
    """
    Create an 'HGVS (HGVSc)' column by combining 'Transcript' and 'Variant (HGVSc)'.
    e.g. NM_000059.3: c.1234A>G
    """
    df["HGVS (HGVSc)"] = df["Transcript"].astype(str) + ":" + df["Variant (HGVSc)"].astype(str)
    return df


def test_variant_validator_batch(hgvs_list):
    """
    Dummy placeholder for a batch validator.
    Replace with your actual batch API calls or logic.

    Here we just return a DataFrame with 'HGVS (HGVSc)' and a 'Status' column.
    """
    results = []
    for hgvs in hgvs_list:
        # Example logic (replace with actual API calls):
        if "c." in hgvs:
            results.append({"HGVS (HGVSc)": hgvs, "Status": "Valid format"})
        else:
            results.append({"HGVS (HGVSc)": hgvs, "Status": "Invalid format"})
    return pd.DataFrame(results)


def validate_variants(df):
    """
    Button-based function to validate variants using an API (or local logic).
    """
    if st.button("Validate Variants"):
        with st.spinner("Validating variants..."):
            # Suppose we call a function that handles multiple HGVS
            results_df = test_variant_validator_batch(df["HGVS (HGVSc)"].tolist())

        st.success("✅ Validation completed!")
        st.dataframe(results_df)

        # Provide CSV download
        csv_data = results_df.to_csv(index=False)
        st.download_button(
            "⬇️ Download Validation Results (CSV)",
            csv_data,
            "validation_results.csv",
            "text/csv",
        )

# -----------------------
# STREAMLIT MAIN INTERFACE
# -----------------------

import streamlit as st
import pandas as pd
import requests

# NOTE:
# 1. Make sure you have the *batch* versions of validate_base_gene and validate_comparison_variant:
#    - validate_base_gene(csv_path) -> returns a DataFrame [Gene, Reference, Message]
#    - validate_comparison_variant(csv_path) -> returns a DataFrame [Transcript, Variant (HGVSc), Gene Symbol, Message]
#
# 2. load_uploaded_variant_file() and validate_variants() can remain as they were, handling a CSV with
#    'Transcript', 'Variant (HGVSc)' -> generating HGVS -> calling an API in bulk, etc.

def main():
    st.set_page_config(layout="wide")
    st.title("🧬 PhenoVariant App (Fixed, Batch Version)")

    # Keep base_df and comp_df in session_state so they persist
    if "base_df" not in st.session_state:
        st.session_state.base_df = None
    if "comp_df" not in st.session_state:
        st.session_state.comp_df = None

    # Tabs for demonstration
    tab_names = ["Validate Base & Comparison", "Validate Uploaded CSV"]
    selected_tab = st.radio("Choose Tab", tab_names)

    # ----------------------------------------------
    # TAB 1: Validate Base & Comparison (Batch Style)
    # ----------------------------------------------
    if selected_tab == "Validate Base & Comparison":
        st.subheader("1. Base Gene Validation (CSV)")
        base_file = st.file_uploader("Upload Base Gene CSV", type=["csv"], key="base_csv_uploader")
        if base_file is not None:
            if st.button("Validate All Base Genes"):
                with st.spinner("Validating All Base Genes..."):
                    # validate_base_gene should return a DataFrame [Gene, Reference, Message]
                    base_df = validate_base_gene(base_file)
                st.session_state.base_df = base_df  # Store in session
                st.success("Base gene validation complete!")
                st.dataframe(base_df)

                # Optional: CSV download
                csv_data = base_df.to_csv(index=False)
                st.download_button(
                    label="Download Base Validation Results (CSV)",
                    data=csv_data,
                    file_name="base_gene_validation_results.csv",
                    mime="text/csv"
                )

        st.subheader("2. Comparison Variant Validation (CSV)")
        comp_file = st.file_uploader("Upload Comparison Variant CSV", type=["csv"], key="comp_csv_uploader")
        if comp_file is not None:
            if st.button("Validate All Comparison Variants"):
                with st.spinner("Validating All Comparison Variants..."):
                    # validate_comparison_variant should return [Transcript, Variant (HGVSc), Gene Symbol, Message]
                    comp_df = validate_comparison_variant(comp_file)
                st.session_state.comp_df = comp_df  # Store in session
                st.success("Comparison variant validation complete!")
                st.dataframe(comp_df)

                # Optional: CSV download
                csv_data = comp_df.to_csv(index=False)
                st.download_button(
                    label="Download Comparison Validation Results (CSV)",
                    data=csv_data,
                    file_name="comparison_variant_validation_results.csv",
                    mime="text/csv"
                )

        st.subheader("3. Compare Base & Comparison")
        # We can compare only if both DataFrames have been set
        if st.session_state.base_df is not None and st.session_state.comp_df is not None:
            if st.button("Compare Base & Comparison"):
                with st.spinner("Comparing..."):
                    compare_df = compare_all_base_and_comparison(
                        st.session_state.base_df,
                        st.session_state.comp_df
                    )
                st.success("Comparison complete!")
                st.dataframe(compare_df)

                # Optional: Download
                csv_data = compare_df.to_csv(index=False)
                st.download_button(
                    label="Download Comparison Results (CSV)",
                    data=csv_data,
                    file_name="base_comparison_results.csv",
                    mime="text/csv"
                )
        else:
            st.info("Upload and validate both Base and Comparison CSVs to enable comparison.")

    # ------------------------------------------------
    # TAB 2: Validate a CSV of Variants (Your Own Logic)
    # ------------------------------------------------
    elif selected_tab == "Validate Uploaded CSV":
        st.subheader("Upload a CSV File for Variant Validation")
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file:
            df = load_uploaded_variant_file(uploaded_file)
            if df is not None:
                # Generate HGVS column
                df = generate_hgvs_column(df)
                st.dataframe(df.head())

                # Validate
                validate_variants(df)

if __name__ == "__main__":
    main()