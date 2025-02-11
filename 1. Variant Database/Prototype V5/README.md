# PhenoVariant App

## Overview
The PhenoVariant App combines a Variant Database and HPO Annotator components into a singular, modular app designed to assist researchers and clinicians in managing, searching, and annotating genetic variants associated with rare diseases. It integrates Human Phenotype Ontology (HPO) terms to enhance variant interpretation.

## Features
- Upload, store, and manage variant data
- Search and filter variants using multiple criteria
- Annotate variants with HPO terms
- Export annotated data for further analysis
- User-friendly web interface

## Installation
### Requirements
- This program was developed on Python 3.11.7.

### Setup
1. Install dependencies:
   ```bash
   pip install pronto
   ```
2. Run the web app:
   ```bash
   streamlit run app_main.py
   ```
   
## Usage
### Uploading Clinical Data
1. Modify the *config.yaml* to the specific paths of the files you want to access.
2. Navigate to the "Configuration" side bar menu.
3. Upload the *config.yaml* file.
5. The system will process and store the data, ready to be queried.

### Searching Variants
1. After standardising the data, use the search bar to query by a category (gene, variant type, etc).
2. Apply filters to refine the search results.

### Annotating with HPO Terms
1. Add relevant medical notes or phenotypes and the system will identify HPO terms to enhance interpretation.
2. Save annotations for future reference.
3. (Optional): First time users may need to upload a *hp.obo* file before using the HPO Annotator tool, which is stored in the 'Output' folder

### Exporting Data
- Annotated variants can be exported as CSV or JSON.


