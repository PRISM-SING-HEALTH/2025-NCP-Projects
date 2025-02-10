import pandas as pd
import requests



def test_variant_validator_batch(variants):
    """
    Validates multiple variants using the Variant Validator API's `hgvs2reference` endpoint.

    This function sends a batch of variants in HGVS format to the Variant Validator API
    and retrieves their corresponding genomic reference positions.

    Parameters:
    -----------
    variants : list
        A list of variant strings in HGVS format to be validated.

    Returns:
    --------
    pandas.DataFrame
        A DataFrame containing validation results with the following columns:
        - 'Variant': The input HGVS variant.
        - 'Start Position': The genomic start position (if available).
        - 'End Position': The genomic end position (if available).
        - 'Sequence': The reference sequence (if available).
        - 'Validated': Boolean indicating if the variant was successfully validated.
        - 'Error': Any error message encountered during validation.

    Notes:
    ------
    - Uses the Variant Validator API (`hgvs2reference` endpoint) via a `GET` request.
    - Handles API responses including successful validation, missing variants (404), and request errors.
    - If the variant is invalid or an error occurs, the 'Error' column will contain the relevant message.
    - Ensures robust error handling using `requests.exceptions.RequestException`.
    - Returns an empty DataFrame if no valid results are obtained.
    """
    # Base URL for the Variant Validator hgvs2reference endpoint
    base_url = "https://rest.variantvalidator.org/VariantValidator/tools/hgvs2reference"

    results = []

    for hgvs_variant in variants:
        # Construct the full URL
        url = f"{base_url}/{hgvs_variant}?content-type=application/json"
        
        try:
            # Send GET request
            response = requests.get(url)

            # Process the response
            if response.status_code == 200:
                response_data = response.json()

                if response_data.get('error'):
                    results.append({
                        'Variant': hgvs_variant,
                        'Start Position': '',
                        'End Position': '',
                        'Sequence': '',
                        'Validated': False,
                        'Error': response_data['error']
                    })
                else:
                    results.append({
                        'Variant': hgvs_variant,
                        'Start Position': response_data.get('start_position', ''),
                        'End Position': response_data.get('end_position', ''),
                        'Sequence': response_data.get('sequence', ''),
                        'Validated': True,
                        'Error': ''
                    })
            elif response.status_code == 404:
                results.append({
                    'Variant': hgvs_variant,
                    'Start Position': '',
                    'End Position': '',
                    'Sequence': '',
                    'Validated': False,
                    'Error': f"Variant not found. HTTP 404."
                })
            else:
                results.append({
                    'Variant': hgvs_variant,
                    'Start Position': '',
                    'End Position': '',
                    'Sequence': '',
                    'Validated': False,
                    'Error': f"HTTP {response.status_code}: {response.text}"
                })
        except requests.exceptions.RequestException as e:
            results.append({
                'Variant': hgvs_variant,
                'Start Position': '',
                'End Position': '',
                'Sequence': '',
                'Validated': False,
                'Error': f"Request error: {e}"
            })

    # Convert results to a DataFrame
    results_df = pd.DataFrame(results)

    return results_df
