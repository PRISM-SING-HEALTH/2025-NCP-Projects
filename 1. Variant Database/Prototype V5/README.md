# PhenoVariant App

## Overview
**PhenoVariant App** is a unified platform designed to help researchers and clinicians manage, search, and annotate genetic variants associated with rare diseases. It integrates the [**FastHPOCR**](https://github.com/tudorgroza/fast_hpo_cr) package to automatically extract phenotype descriptions during data import, enabling fast and accurate phenotype identification.

The app features a **Variant Database** that automates the traditionally slow, manual curation of variant data. Designed with user-friendliness in mind, it streamlines variant data management while improving efficiency. Additionally, the app standardises genetic variant data files, enhancing querying capabilities for faster, more reliable searches.

The **PhenoVariant App** was developed during a six-week internship at **KK Women's and Children's Hospital (KKH), Singapore**, as part of the **New Colombo Plan**. Two students from **Curtin University, Bentley**, collaborated on this project to support end users at KKH by addressing a specific challenge within the broader goal of accelerating rare disease diagnosis worldwide.

### Project Students
- [Angelo Lagahit](https://www.linkedin.com/in/angelo-lagahit/)
- [Sze Wei Shong](https://www.linkedin.com/in/sze-wei-shong/)

## Installation
The **PhenoVariant App** is a standalone Windows executable, requiring no additional installation steps or dependencies. Simply download and run the executable file.\
**To run the app:**
1. Download *PhenoVariant.zip*
2. Extract contents from the zip file
3. Double-click *run.exe* to launch

### Developer Setup
For those who wish to modify or run the app from source, follow these steps.

#### Requirements
|Package Name|Description|Justification|Version for Python 3.11.7|
|------------|-----------|-------------|-------------------------|
|Streamlit|Framework for building interactive web applications with Python|Graphical user interface|1.13.0|
|Altair|Declarative statistical visualisation library for Python|Dependancy for Streamlit|4.0.0|
|Pronto|Library for working with ontologies in Python|Parsing, editing, and querying ontology formats like OBO|2.5.8|
|OpenPyXL|Reading and writing Excel (.xlsx) files|Reading clinical excel files|3.1.5|
|PyYAML|Allows Python applications to read, write, and manipulate YAML configuration files|File config management|6.0.2|

- Python 3.11.7.
- Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
- Run the Python script:
   ```bash
   streamlit run app_main.py
   ```
- Package application:
   ```bash
   pip install cx_Freeze
   cxFreeze --script run.py
   ```
## Usage

### Video Demo
A video demonstration is available [here](https://youtu.be/fOC2-GlDFKM).

### Uploading Clinical Data
1. Modify the *config.yaml* to the specific paths of the files you want to access.
2. Navigate to the "Configuration" side bar menu.
3. Upload the *config.yaml* file.
4. The system will process and store the data, ready to be queried.

### Standardising Clinical Data
5. Select the **Standardise Data** button, which will combine all the data into a single dataframe with the new standard columns.

### Query
6. Select the **Query Data** button.
7. Use the drop-down menu to select a category (multiple allowed) to query.
8. Enter a term to query in the search box, or alternatively, use the drop-down menu options.
9. *Optional: Select between AND/OR filters to refine search.*
10. *Optional: Download data as CSV.*

### Annotating with HPO Terms
1. Add relevant medical notes or phenotypes and the system will identify HPO terms to enhance interpretation.
2. Save annotations for future reference.

## Maintanence
New terms are constantly being added to the ontology. Between December 2022 and February 2024, there was an increase of 1303 terms, i.e. ~7% increase [(Source)](https://academic.oup.com/bioinformatics/article/40/7/btae406/7698025).

### Updating HPO Release
To ensure the program is up-to-date, it is recommended to update the ontology every 6 months.
1. Download the latest version of **hp.obo** from [OBO Foundry](https://obofoundry.org/ontology/hp.html).
2. In the **PhenoVariant App**, navigate to the "Configuration" side bar menu.
3. Upload the **hp.obo** file.

The upload process may take several minutes to complete. Once the process is finished, a **hp.index** file will be generated and stored in the "output" folder of the program.

### FastHPOCR
Please refer to [**FastHPOCR**](https://github.com/tudorgroza/fast_hpo_cr) for any new updates.

### VariantValidator REST API
The following [VariantValidator REST API](https://rest.variantvalidator.org/) are used in the program:
- gene2transcripts_v2
- variantvalidator

## Configuration Guide
1. Modify the **config.yaml** with the path locations of the desired folders you want to access.
2. In **app_main.py**, modify **line34** with the path location of the **config.yaml** file.

### Test Environment
Due to being unable to test on actual network laptops, we emulated the environment using the following directory structure:
- Mock_Local_Drive
  - PhenoVariant
- Mock_Shared_Drive
  - External_Drive
    - Invitae_List
  - Internal_Drive
    - ATM_List
    - Clinic_List
    - Lab_Case_List
  - Research_Drive
    - Research_List

## Future Work
### Offline VariantValidator Feature
We focused on implementing the online feature before approaching an offline solution.
**Starting points:**
- [SeqRepo](https://github.com/biocommons/biocommons.seqrepo)
- [ClinVar VCF](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/)
- [VariantValidator Repo](https://github.com/openvar/variantValidator/blob/master/README.md)
