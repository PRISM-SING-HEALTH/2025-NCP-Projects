import streamlit as st
from variant.dataframe import *
from variant.query import *
from variant.validator import *
from variant.streamlit_func import *
from variant.standardise import *



# ===============================
# STREAMLIT UI CONFIGURATION
# ===============================

# Set up Streamlit page layout
st.set_page_config(layout="wide")
st.title("🧬 PhenoVariant App")

# Create navigation tabs
tab1, tab2, tab3 = create_navigation()



# =======================================
# TAB 1: VARIANT DATABASE
# =======================================

with tab1:
    # ------------------------------------
    # 1. CONFIGURATION FILE (YAML UPLOAD)
    # ------------------------------------
    config = load_yaml_configuration()

    # -----------------------------------------
    # 2. NAVIGATION WITHIN VARIANT DATABASE TAB
    # -----------------------------------------
    options = ["Load Data", "Standardise Data", "Query Data", "Validate Variants"]
    variant_tab = st.radio("Select option:", options, horizontal=False)

    # ----------------------------------------------------
    # 3. INITIALISE STANDARD COLUMN NAMES (if YAML loaded)
    # ----------------------------------------------------
    if config:
        standard_columns = initialise_standard_columns()
        base_path = config.get('base_path', "")
        files = config.get('files', {})
        
        # ----------------------------
        # OPTION 1: LOAD DATA SECTION
        # ----------------------------
        if variant_tab == "Load Data":
            st.header("📂 Load Variant Data")

            # Load data
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

        # -----------------------------------
        # OPTION 2: STANDARDISE DATA SECTION
        # -----------------------------------
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

        # -----------------------------
        # OPTION 3: QUERY DATA SECTION
        # -----------------------------
        elif variant_tab == "Query Data":
            st.header("🔍 Query Variant Data")

            if "Combined" in st.session_state:
                query(st.session_state["Combined"])
            else:
                st.warning("⚠️ Please standardise and combine data before querying.")

        # ------------------------------------
        # OPTION 4: VALIDATE VARIANTS SECTION
        # ------------------------------------
        elif variant_tab == "Validate Variants":
            st.header("✅ Variant Validator")

            uploaded_file = st.file_uploader("Upload CSV file with variants", type=["csv"])

            if uploaded_file:
                df = load_uploaded_variant_file(uploaded_file)

                if df is not None:
                    df = generate_hgvs_column(df)
                    validate_variants(df)

# ========================
# VARIANT DATABASE FOOTER
# ========================
    st.markdown("---")
    st.markdown("💡 **Tip:** Upload `config.yaml`, standardise the data, then query results!")


    
# ======================
# TAB 2: HPO ANNOTATION
# ======================
with tab2:
    # ----------------------------
    # 1. UPLOAD AND SAVE HPO FILE
    # ----------------------------
    hpo_path = upload_hpo_file()

    # -----------------------------
    # 2. CONFIGURE INDEX OPTIONS
    # -----------------------------
    hpo_indexing_options(hpo_path)

    # -------------------------
    # 3. ANNOTATE MEDICAL TEXT
    # -------------------------
    annotate_text()

    # =================
    # FOOTER
    # =================
    st.markdown("---")
    st.markdown("💡 **Tip:** Upload `hp.obo`, generate the index, then annotate text!")



# ======================
#  TAB 3: ABOUT SECTION
# ======================
with tab3:
    display_about_section()
