import pandas as pd
import requests



def test_variant_validator_batch(variants):
    """
    Tests multiple variants using the Variant Validator API's hgvs2reference endpoint.

    Args:
        variants (list): A list of variants in HGVS format to validate.

    Returns:
        pd.DataFrame: A DataFrame containing the results.
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
