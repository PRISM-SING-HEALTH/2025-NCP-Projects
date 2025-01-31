# PhenoVariant App

## Overview
The PhenoVariant App combined a Variant Database and HPO Annotator components into a singular, modular app designed to assist researchers and clinicians in managing, searching, and annotating genetic variants associated with rare diseases. It integrates Human Phenotype Ontology (HPO) terms to enhance variant interpretation.

## Features
- Upload, store, and manage variant data
- Search and filter variants using multiple criteria
- Annotate variants with HPO terms
- Export annotated data for further analysis
- User-friendly web interface

## Installation
### Requirements
- This program was developed on Python 3.13.1.

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
1. Navigate to the "Upload" section.
2. Upload data in CSV or XLSX format.
3. The system will process and store the data.

### Searching Variants
1. Use the search bar to query by gene, variant type, or associated disease.
2. Apply filters to refine the search results.
3. Click on a variant to view detailed annotations.

### Annotating with HPO Terms
1. Add relevant HPO terms to enhance interpretation.
2. Save annotations for future reference.

### Exporting Data
- Annotated variants can be exported as CSV or JSON for downstream analysis.


