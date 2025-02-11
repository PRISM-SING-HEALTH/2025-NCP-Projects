import os
import json
import yaml
import streamlit as st
import pandas as pd
from variant.validator import *
from variant.IndexHPO import *
from variant.HPOAnnotator import HPOAnnotator



# Define paths for storing HPO index files
OUTPUT_FOLDER = "output"
INDEX_FILE = os.path.join(OUTPUT_FOLDER, "hp.index")



def load_yaml_configuration():
    """
    Handles YAML file upload and parsing for configuration.

    Returns:
    --------
    dict or None
        A dictionary containing configuration details if successfully loaded, else None.
    """
    st.sidebar.header("🛠 Configuration")
    st.sidebar.subheader("Variant Database")

    yaml_file = st.sidebar.file_uploader("Upload `config.yaml` file", type=["yaml", "yml"])
    if yaml_file:
        try:
            config = yaml.safe_load(yaml_file)
            st.sidebar.success("✅ YAML configuration loaded successfully!")
            return config
        except Exception as e:
            st.sidebar.error(f"❌ Failed to load YAML: {e}")
    
    return None



def initialise_standard_columns():
    """
    Initialises and returns the standard column names used for data standardisation.

    Returns:
    --------
    list
        A list of standard column names.
    """
    standard_columns = [
        'MRN', 'Patient Name', 'Var Count', 'Var Number', 'Phenotype','HPO Terms', 'Solved Status',
        'Gene', 'HGVSg', 'Transcript', 'Variant (HGVSc)', 'HGVSp', 'Type', 'Zygosity', 'Inheritance',
    ]

    return standard_columns



def create_navigation():
    """
    Creates navigation tabs for the Streamlit application.

    Returns:
    --------
    tuple
        A tuple containing Streamlit tabs for navigation.
    """
    navigation_tab = st.tabs(["🧬 Variant Database", "🔍 HPO Annotation", "📚 About"])
    
    return navigation_tab



def extract_hpo_terms(df, phenotype_column):
    """
    Extracts HPO terms from the Phenotype column using HPOAnnotator.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing a Phenotype column.
    phenotype_column : str
        Name of the column containing free-text phenotype descriptions.

    Returns:
    --------
    pandas.DataFrame
        The updated DataFrame with an additional 'HPO Terms' column.
    """
    if phenotype_column not in df.columns:
        print(f"⚠️ Column '{phenotype_column}' not found in DataFrame.")
        return df

    # Ensure the HPO index is available
    if not os.path.exists(INDEX_FILE):
        print("⚠️ HPO Index not found! Ensure `hp.obo` is uploaded and indexed.")
        return df

    annotator = HPOAnnotator(INDEX_FILE)

    # Function to extract HPO terms
    def get_hpo_terms(phenotype_text):
        if pd.isna(phenotype_text) or not isinstance(phenotype_text, str):
            return ""
        annotations = annotator.annotate(phenotype_text)
        return ", ".join([f"{ann.hpoUri} ({ann.hpoLabel})" for ann in annotations])

    # Apply HPO extraction to the Phenotype column
    df["HPO Terms"] = df[phenotype_column].apply(get_hpo_terms)
    
    # Convert HPO Terms to a vertical list (newline-separated)
    df["HPO Terms"] = df["HPO Terms"].apply(lambda x: "\n".join(x.split(", ")) if isinstance(x, str) else x)


    return df



def load_variant_data(config, base_path):
    """
    Loads variant data from Excel files and extracts HPO terms at load time.

    Parameters:
    -----------
    config : dict
        Dictionary containing file paths from the YAML configuration.
    base_path : str
        The base directory where the files are stored.

    Returns:
    --------
    dict
        A dictionary of loaded pandas DataFrames.
    """
    try:
        with st.spinner("Loading data..."):
            # Reading files
            lab_cases_df = pd.read_excel(f"{base_path}{config['files']['lab_cases']}", sheet_name='Sheet1', header=0)
            invitae_summary_df = pd.read_excel(f"{base_path}{config['files']['invitae_summary']}", sheet_name='Invitae list header', header=0)
            clinical_summary_df = pd.read_excel(f"{base_path}{config['files']['clinical_summary']}", sheet_name='11 Dec', header=0)
            research_summary_df = pd.read_excel(f"{base_path}{config['files']['research_summary']}", sheet_name='Overall List', header=2)

            # Handling unconventional ATM summary format
            atm_summary_df = pd.read_excel(f"{base_path}{config['files']['atm_summary']}", sheet_name='SUMMARY', header=None)
            atm_summary_df_filtered = atm_summary_df.iloc[8:17].reset_index(drop=True)
            atm_structured_df = atm_summary_df_filtered.set_index(0).T.reset_index(drop=True)

            # Extract HPO terms from Phenotype columns
            lab_cases_df = extract_hpo_terms(lab_cases_df, "Phenotype")
            clinical_summary_df = extract_hpo_terms(clinical_summary_df, "Medical Prob description")
            research_summary_df = extract_hpo_terms(research_summary_df, "Phenotype")
            #invitae_summary_df = extract_hpo_terms(invitae_summary_df, "Phenotype") # Does not contain phenotype column currently
            #atm_structured_df = extract_hpo_terms(atm_structured_df, "Phenotype") # Does not contain phenotype column currently

            # Store imported dataframes in a dictionary
            dataframes = {
                "Lab Cases": lab_cases_df,
                "ATM Summary": atm_structured_df,
                "Invitae Summary": invitae_summary_df,
                "Clinical Summary": clinical_summary_df,
                "Research Summary": research_summary_df,
            }

        return dataframes

    except FileNotFoundError as e:
        st.error(f"❌ File not found: {e}")
        return None
    except ValueError as e:
        st.error(f"❌ Error reading sheet or invalid data format: {e}")
        return None



def display_loaded_dataframes(dataframes):
    """
    Displays the loaded dataframes in Streamlit.

    Parameters:
    -----------
    dataframes : dict
        A dictionary of pandas DataFrames.
    """
    if dataframes:
        for name, df in dataframes.items():
            st.write(f"### {name}", df.head())



def load_uploaded_variant_file(uploaded_file):
    """
    Loads and validates the uploaded CSV file containing variant data.

    Parameters:
    -----------
    uploaded_file : UploadedFile
        The CSV file uploaded by the user.

    Returns:
    --------
    pd.DataFrame or None
        A DataFrame if the file is valid, otherwise None.
    """
    df = pd.read_csv(uploaded_file)

    # Ensure required columns exist
    required_columns = {'Transcript', 'Variant (HGVSc)'}
    if not required_columns.issubset(df.columns):
        st.error("❌ Uploaded file must contain 'Transcript' and 'Variant (HGVSc)' columns.")
        return None

    st.success("✅ File uploaded successfully!")
    return df



def validate_variants(df):
    """
    Validates variants using the Variant Validator API and displays results in Streamlit.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the 'HGVS (HGVSc)' column for validation.

    Returns:
    --------
    None
    """
    if st.button("Validate Variants"):
        with st.spinner("Validating variants..."):
            results_df = test_variant_validator_batch(df['HGVS (HGVSc)'].tolist())

        st.success("✅ Validation completed!")
        st.dataframe(results_df)

        # Provide CSV download option
        csv_data = results_df.to_csv(index=False)
        st.download_button("⬇️ Download Validation Results (CSV)", csv_data, "validation_results.csv", "text/csv")



def upload_hpo_file():
    """
    Handles HPO Ontology file upload and saves it locally.

    Returns:
    --------
    str or None
        Path to the saved HPO file if uploaded successfully, else None.
    """
    st.sidebar.subheader("HPO Annotation")
    uploaded_file = st.sidebar.file_uploader("Upload `hp.obo` file", type=["obo"])

    if uploaded_file:
        hpo_path = os.path.join(OUTPUT_FOLDER, "hp.obo")
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        with open(hpo_path, "wb") as f:
            f.write(uploaded_file.read())

        st.sidebar.success(f"`hp.obo` uploaded successfully!")
        return hpo_path

    return None



def hpo_indexing_options(hpo_path):
    """
    Displays HPO indexing configuration options and generates an HPO index.

    Parameters:
    -----------
    hpo_path : str
        Path to the uploaded HPO Ontology file.

    Returns:
    --------
    None
    """
    if not hpo_path:
        return

    st.sidebar.header("⚙️ Indexing Options")

    # Root Concept Selection
    root_concept_choices = {
        "HP:0000118": "Phenotypic abnormality", "HP:0000707": "Nervous system",
        "HP:0001574": "Growth", "HP:0000478": "Eye", "HP:0000598": "Ear",
        "HP:0000119": "Metabolism/Homeostasis", "HP:0003011": "Muscle", "HP:0000769": "Voice",
        "HP:0001507": "Skeletal", "HP:0001939": "Blood & Hematology", "HP:0001626": "Cardiovascular",
        "HP:0000818": "Breast", "HP:0001392": "Digestive system", "HP:0002086": "Respiratory",
        "HP:0002715": "Endocrine", "HP:0000924": "Genitourinary", "HP:0002664": "Immune system",
        "HP:0000767": "Integument (Skin, Hair, Nails)", "HP:0025031": "Prenatal & Birth",
        "HP:0001197": "Neoplasm", "HP:0032443": "Cellular phenotype",
        "HP:0001871": "Immune system", "HP:0000152": "Mouth & Dentition", "HP:0011446": "Connective tissue"
    }

    selected_root_concepts = st.sidebar.multiselect(
        "Select Root Concepts",
        options=list(root_concept_choices.keys()),
        default=list(root_concept_choices.keys())  # Pre-select all
    )

    # Boolean Configuration Settings
    allow_acronyms = st.sidebar.checkbox("Allow 3-letter acronyms (e.g., 'VUR')", value=True)
    include_categories = st.sidebar.checkbox("Include top-level category", value=True)
    allow_duplicates = st.sidebar.checkbox("Allow duplicate entries", value=False)

    if st.sidebar.button("🔧 Generate Index"):
        with st.spinner("Indexing HPO terms..."):
            index_config = {
                "rootConcepts": selected_root_concepts,
                "allow3LetterAcronyms": allow_acronyms,
                "includeTopLevelCategory": include_categories,
                "allowDuplicateEntries": allow_duplicates
            }

            index_hpo = IndexHPO(hpo_path, OUTPUT_FOLDER, indexConfig=index_config)
            index_hpo.index()

        st.sidebar.success("✅ HPO Index Created!")



def annotate_text():
    """
    Handles text annotation using the generated HPO index.

    Returns:
    --------
    None
    """
    st.header("📝 Annotate Medical Text")
    text_input = st.text_area("Enter medical text", "The patient was diagnosed with vesicoureteral reflux and muscle weakness.")

    if st.button("🔍 Annotate"):
        if not os.path.exists(INDEX_FILE):
            st.error("❌ No index found! Please upload `hp.obo` and generate the index first.")
        else:
            with st.spinner("Processing..."):
                annotator = HPOAnnotator(INDEX_FILE)
                annotations = annotator.annotate(text_input)

            if annotations:
                st.success("✅ HPO Concepts Found!")

                # Convert annotations to structured data
                annotation_data = [{"HPO ID": ann.hpoUri, "Label": ann.hpoLabel, "Text Span": ann.textSpan} for ann in annotations]

                # Display annotations
                for ann in annotation_data:
                    st.write(f"🧬 **{ann['HPO ID']}** - {ann['Label']} (Found: '{ann['Text Span']}')")

                # Convert to DataFrame
                df = pd.DataFrame(annotation_data)

                # JSON & CSV Download Buttons
                json_data = json.dumps(annotation_data, indent=4)
                csv_data = df.to_csv(index=False).encode("utf-8")

                st.download_button("⬇️ Download Annotations (JSON)", json_data, "annotations.json", "application/json")
                st.download_button("⬇️ Download Annotations (CSV)", csv_data, "annotations.csv", "text/csv")

            else:
                st.warning("⚠️ No HPO concepts detected.")



def display_about_section():
    """
    Displays the About section of the PhenoVariant App.

    This section provides an overview of the project, credits contributors, 
    and describes the Variant Database and HPO Text Annotator functionalities.

    Returns:
    --------
    None
    """
    st.header("📚 About")

    # Project Overview
    st.markdown("""
    The **PhenoVariant App** is a modular tool for querying, annotating, and validating
    genomic variants while ensuring privacy and preserving data access.
    """)

    # Acknowledgments
    st.markdown("""
    **Developers:**  
    - **Variant Database:** Developed by 2025 New Colombo Plan interns **Angelo Lagahit & Sze Wei Shong** (Curtin University).
    - **HPO Annotation Model:** Developed by **Tudor Groza**, integrated by the interns.
    """)

    # Variant Database - Features Overview
    st.subheader("🧬 Variant Database")
    st.markdown("""
    - **Consolidates & harmonises variant data**
    - **Supports multi-level querying** (Gene, Phenotype, Variant Type, Solved Status)
    - **Layered filtering, export, and external validation (VariantValidator)**
    """)

    # HPO Text Annotator - Features Overview
    st.subheader("🔍 HPO Text Annotator")
    st.markdown("""
    - **Extracts HPO concepts from medical text using high-speed NLP (FastHPOCR)**
    - **Provides structured phenotype annotation for clinical diagnostics**
    - This script utilises code from the FastHPOCR project, developed by Tudor Groza and collaborators, without modifications.
    - GitHub Repository: https://github.com/tudorgroza/fast_hpo_cr
    - All credit for the original implementation goes to the authors of FastHPOCR.
    """)
