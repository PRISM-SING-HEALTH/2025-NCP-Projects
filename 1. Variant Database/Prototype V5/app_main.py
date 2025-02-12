import streamlit as st
from variant.dataframe import *
from variant.query import *
from variant.validator import *
from variant.streamlit_func import *
from variant.standardise import *
from variant.access import *

##########################
# Example Compare Function
##########################
def compare_all_base_and_comparison(base_df, comp_df):
    """
    Compare rows from base_df to comp_df. This matches row i in base_df
    with row i in comp_df. Returns a new DataFrame with combined info:
      - 'Gene', 'Reference'
      - 'Transcript', 'Variant (HGVSc)', 'Gene Symbol'
      - 'ComparisonResult'
    """
    results = []
    max_len = max(len(base_df), len(comp_df))

    for i in range(max_len):
        # Get base info if row i exists
        if i < len(base_df):
            base_gene = base_df.loc[i, "Gene"] if "Gene" in base_df.columns else None
            base_ref  = base_df.loc[i, "Reference"] if "Reference" in base_df.columns else None
        else:
            base_gene = None
            base_ref  = None

        # Get comparison info if row i exists
        if i < len(comp_df):
            transcript = comp_df.loc[i, "Transcript"] if "Transcript" in comp_df.columns else None
            variant    = comp_df.loc[i, "Variant (HGVSc)"] if "Variant (HGVSc)" in comp_df.columns else None
            comp_sym   = comp_df.loc[i, "Gene Symbol"] if "Gene Symbol" in comp_df.columns else None
        else:
            transcript = None
            variant    = None
            comp_sym   = None

        comparison_msg = compare_base_and_comparison(base_ref, comp_sym)

        results.append({
            "Gene": base_gene,
            "Reference": base_ref,
            "Transcript": transcript,
            "Variant (HGVSc)": variant,
            "Gene Symbol": comp_sym,
            "ComparisonResult": comparison_msg
        })

    return pd.DataFrame(results)


##########################
# STREAMLIT MAIN APP
##########################

# ===============================
# STREAMLIT UI CONFIGURATION
# ===============================
st.set_page_config(layout="wide")
st.title("🧬 PhenoVariant App")

# Create navigation tabs
tab1, tab2, tab3 = create_navigation()

# =======================================
# TAB 1: VARIANT DATABASE
# =======================================
with tab1:
    # 1. CONFIGURATION FILE (YAML UPLOAD)
    config = load_yaml_configuration()

    # 2. OPTIONAL FILE SYNC
    if config:
        base_path = config.get('base_path', "")
        config_file_path = "C:/Users/lagah/Documents/dev/app/Mock_Local_Drive/config.yaml"

        st.subheader("📂 File Syncing Option")
        enable_sync = st.checkbox("Sync files to the shared folder before loading data?", value=False)

        if enable_sync:
            with st.spinner("Syncing files to shared folder..."):
                sync_files_to_common_folder(config_file_path)
            st.success("✅ File sync completed.")

    # 3. NAVIGATION WITHIN VARIANT DATABASE TAB
    options = ["Load Data", "Standardise Data", "Query Data", "Validate Variants"]
    variant_tab = st.radio("Select option:", options, horizontal=False)

    # 4. INITIALISE STANDARD COLUMN NAMES
    if config:
        standard_columns = initialise_standard_columns()
        base_path = config.get('base_path', "")
        files = config.get('files', {})

        # 4.1 LOAD DATA
        if variant_tab == "Load Data":
            st.header("📂 Load Variant Data")
            if config:
                dataframes = load_variant_data(config, base_path)
                if dataframes:
                    # Convert to string format
                    dataframes = convert_dataframes_to_string(dataframes)
                    # Store in session state
                    st.session_state["dataframes"] = dataframes
                    st.success("✅ Data successfully loaded!")
                    # Display loaded data
                    display_loaded_dataframes(dataframes)
            else:
                st.warning("⚠️ Please upload a YAML config file.")

        # 4.2 STANDARDISE DATA
        elif variant_tab == "Standardise Data":
            st.header("🛠 Standardise Data")
            if "dataframes" in st.session_state:
                try:
                    with st.spinner("Standardising and combining data..."):
                        dataframes = st.session_state["dataframes"]
                        combined_df = standardise_data(dataframes, standard_columns)
                        st.session_state["Combined"] = combined_df
                        st.success("✅ Data successfully standardised and combined!")
                        # Display results
                        st.write("### Combined Dataframe")
                        st.write(combined_df)
                except Exception as e:
                    st.error(f"❌ Failed to standardise data: {e}")
            else:
                st.warning("⚠️ Please load data first.")

        # 4.3 QUERY DATA
        elif variant_tab == "Query Data":
            st.header("🔍 Query Variant Data")
            if "Combined" in st.session_state:
                query(st.session_state["Combined"])
            else:
                st.warning("⚠️ Please standardise and combine data before querying.")

        # 4.4 VARIANT VALIDATOR
        elif variant_tab == "Validate Variants":
            st.header("✅ Variant Validator")

            # CSV uploader
            single_file = st.file_uploader(
                "Upload a single CSV from the QUERY DATA tab with 'Gene', 'Transcript', and 'Variant (HGVSc)' columns",
                type=["csv"],
                key="single_validator_csv"
            )

            if single_file:
                if st.button("Validate & Compare All Rows"):
                    with st.spinner("Validating & Comparing..."):
                        results_df = validate_both_in_one(single_file)
                    st.success("Validation complete!")
                    st.dataframe(results_df)

                    # Optional download
                    csv_data = results_df.to_csv(index=False)
                    st.download_button(
                        "Download Combined Results (CSV)",
                        data=csv_data,
                        file_name="combined_validation_results.csv",
                        mime="text/csv"
                    )

# ========================
# VARIANT DATABASE FOOTER
# ========================
    st.markdown("---")
    st.markdown("💡 **Tip:** Upload `config.yaml`, standardise the data, then query results!")

# ======================
# TAB 2: HPO ANNOTATION
# ======================
with tab2:
    hpo_path = upload_hpo_file()
    hpo_indexing_options(hpo_path)
    annotate_text()
    st.markdown("---")
    st.markdown("💡 **Tip:** Upload `hp.obo`, generate the index, then annotate text!")

# ======================
#  TAB 3: ABOUT SECTION 
# ======================
with tab3:
    display_about_section()
