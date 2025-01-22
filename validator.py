import pandas as pd
import os
import requests

def validate_variants(file_path, output_path):
    """
    Validates genetic variants using the VariantValidator API (hgvs2reference endpoint).

    Args:
        file_path (str): Path to the input Excel file containing variants.
        output_path (str): Path to save the validation results.

    Returns:
        None
    """
    try:
        # Load the exported data
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        df = pd.read_excel(file_path)

        # Ensure the required column is present
        if 'HGVSc' not in df.columns:
            raise ValueError("Missing required column: 'HGVSc'")

        # Prepare to store validation results
        validation_results = []

        # Iterate over rows to validate each variant
        print("Validating variants...")
        for index, row in df.iterrows():
            try:
                hgvs_c = row['HGVSc']

                # Construct the API URL
                api_url = f"https://rest.variantvalidator.org/VariantValidator/tools/hgvs2reference/{hgvs_c}?content-type=text/xml"

                # Make the API request
                response = requests.get(api_url, headers={"accept": "text/xml"})
                if response.status_code == 200:
                    # Successful validation
                    validation_results.append({
                        'HGVSc': hgvs_c,
                        'Validation Status': 'Success',
                        'Message': 'Validation successful'
                    })
                elif response.status_code == 404:
                    # Variant not found
                    validation_results.append({
                        'HGVSc': hgvs_c,
                        'Validation Status': 'Failed',
                        'Message': 'Variant not found (404). Check HGVS notation.'
                    })
                else:
                    # Other errors
                    validation_results.append({
                        'HGVSc': hgvs_c,
                        'Validation Status': 'Failed',
                        'Message': f"Error {response.status_code}: {response.text}"
                    })
            except Exception as e:
                validation_results.append({
                    'HGVSc': row['HGVSc'],
                    'Validation Status': 'Error',
                    'Message': f"Error during validation: {e}"
                })

        # Save results to an output file
        results_df = pd.DataFrame(validation_results)
        results_df.to_excel(output_path, index=False)
        print(f"Validation results saved to {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
