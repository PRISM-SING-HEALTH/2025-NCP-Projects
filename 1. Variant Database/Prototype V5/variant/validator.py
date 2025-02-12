import pandas as pd
import requests



def compare_base_and_comparison(base_reference, comparison_gene_symbol):
    """
    Compare two gene identifiers for equality.

    Parameters
    ----------
    base_reference : str or None
        The gene symbol (or other reference) derived from the base validation process.
        May be None if validation failed or the symbol could not be retrieved.
    comparison_gene_symbol : str or None
        The gene symbol derived from the comparison variant validation process.
        May be None if validation failed or the symbol could not be retrieved.

    Returns
    -------
    str
        A text message describing the result:
        - If either parameter is None, indicates that comparison cannot be made.
        - If both match (case-insensitive), returns a "Match" message.
        - Otherwise, returns a "Mismatch" message.
    """
    if base_reference is None or comparison_gene_symbol is None:
        message = "Comparison cannot be made because one or both gene values are missing."
        return message

    if str(base_reference).strip().upper() == str(comparison_gene_symbol).strip().upper():
        message = (
            f"Match: Base gene '{base_reference}' matches "
            f"comparison gene symbol '{comparison_gene_symbol}'."
        )
        return message
    else:
        message = (
            f"Mismatch: Base gene '{base_reference}' does NOT match "
            f"comparison gene symbol '{comparison_gene_symbol}'."
        )
        return message



def compare_all_base_and_comparison(base_df, comp_df):
    """
    Perform a row-by-row comparison of gene symbols from two DataFrames.

    For each row index i, this function retrieves:
        - A base gene and reference from `base_df` (columns: "Gene", "Reference")
        - A transcript, variant, and comparison gene symbol from `comp_df`
          (columns: "Transcript", "Variant (HGVSc)", "Gene Symbol")
    Then it calls the single-record `compare_base_and_comparison` function
    to determine if the base reference matches the comparison gene symbol.

    Parameters
    ----------
    base_df : pandas.DataFrame
        A DataFrame containing at least two columns:
            "Gene" and "Reference".
        May have fewer or more rows than comp_df.
    comp_df : pandas.DataFrame
        A DataFrame containing at least three columns:
            "Transcript", "Variant (HGVSc)", and "Gene Symbol".
        May have fewer or more rows than base_df.

    Returns
    -------
    pandas.DataFrame
        A new DataFrame with the following columns:
            "Gene",
            "Reference",
            "Transcript",
            "Variant (HGVSc)",
            "Gene Symbol",
            "ComparisonResult"
        Each row i in the output corresponds to row i of base_df
        compared with row i of comp_df. If one DataFrame has fewer
        rows than the other, the missing values are set to None.

    Notes
    -----
    This function relies on the helper:
        compare_base_and_comparison(base_reference, comparison_gene_symbol)
    which performs the actual string comparison for each pair of gene symbols.
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



def validate_both_in_one(csv_path):
    """
    Validate and compare both base genes and comparison variants from a single CSV.

    This function reads a CSV file that must contain the columns:
    'Gene', 'Transcript', and 'Variant (HGVSc)'. For each row:

    1. Base Gene Lookup:
       Queries the VariantValidator "gene2transcripts_v2" endpoint using the
       'Gene' value to retrieve the top-level gene symbol (usually found under
       "current_symbol" or "requested_symbol").

    2. Comparison Variant Lookup:
       Queries the VariantValidator "variantvalidator" endpoint using a combined
       "<Transcript>:<Variant (HGVSc)>" string to retrieve the 'gene_symbol'.

    3. Comparison:
       Uses the single-record compare_base_and_comparison() function to check
       whether the retrieved base gene symbol and the comparison gene symbol match.

    Parameters
    ----------
    csv_path : str or file-like
        The path to the CSV file or a file-like object containing the columns
        'Gene', 'Transcript', and 'Variant (HGVSc)'.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the following columns:
            - "Gene": The original 'Gene' value from the CSV.
            - "BaseGeneSymbol": The top-level gene symbol obtained from the base API call.
            - "Transcript": The original 'Transcript' value from the CSV.
            - "Variant (HGVSc)": The original 'Variant (HGVSc)' value from the CSV.
            - "ComparisonGeneSymbol": The gene_symbol obtained from the comparison API call.
            - "ComparisonResult": A message indicating whether they matched or if any error occurred.

    Notes
    -----
    - If either the base or comparison API call fails, or if the symbol is missing,
      the corresponding error message is stored in the "ComparisonResult" column.
    - If the CSV file is empty or lacks the required columns, the function returns
      a one-row DataFrame describing the problem.
    - This function relies on compare_base_and_comparison() for the final matching logic.
    """

    # Prepare list to store row-by-row results
    results = []

    # Attempt reading the CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return pd.DataFrame([{
            "Gene": None,
            "BaseGeneSymbol": None,
            "Transcript": None,
            "Variant (HGVSc)": None,
            "ComparisonGeneSymbol": None,
            "ComparisonResult": f"Error reading CSV: {e}"
        }])

    # Check required columns
    required_cols = {"Gene", "Transcript", "Variant (HGVSc)"}
    if not required_cols.issubset(df.columns):
        return pd.DataFrame([{
            "Gene": None,
            "BaseGeneSymbol": None,
            "Transcript": None,
            "Variant (HGVSc)": None,
            "ComparisonGeneSymbol": None,
            "ComparisonResult": (
                "Error: CSV must contain 'Gene', 'Transcript', and 'Variant (HGVSc)' columns."
            )
        }])

    if df.empty:
        return pd.DataFrame([{
            "Gene": None,
            "BaseGeneSymbol": None,
            "Transcript": None,
            "Variant (HGVSc)": None,
            "ComparisonGeneSymbol": None,
            "ComparisonResult": "Error: CSV is empty."
        }])

    # Loop over each row
    for idx, row in df.iterrows():
        gene_query = row["Gene"]
        transcript = row["Transcript"]
        variant_hgvsc = row["Variant (HGVSc)"]

        # -------------------------------------------------------
        # 1) BASE: Query gene2transcripts_v2 to get gene symbol
        # -------------------------------------------------------
        base_symbol = None
        base_symbol_error = None
        try:
            base_url = (
                "https://rest.variantvalidator.org/VariantValidator/tools/gene2transcripts_v2/"
                f"{gene_query}/mane_select/refseq/GRCh38?content-type=application%2Fjson"
            )
            base_resp = requests.get(base_url)
            if base_resp.status_code == 200:
                data = base_resp.json()
                if isinstance(data, list) and len(data) > 0:
                    # typical top-level gene symbol is "current_symbol" or "requested_symbol"
                    first_record = data[0]
                    base_symbol = first_record.get("current_symbol") or first_record.get("requested_symbol")
                    if not base_symbol:
                        base_symbol_error = "Could not find 'current_symbol' or 'requested_symbol' in base JSON."
                else:
                    base_symbol_error = "Base API response was empty or not a list."
            else:
                base_symbol_error = (
                    f"Base API call failed with status: {base_resp.status_code}"
                )
        except Exception as e:
            base_symbol_error = f"Error during base gene API call: {e}"

        # -------------------------------------------------------
        # 2) COMPARISON: Query variantvalidator to get gene_symbol
        # -------------------------------------------------------
        comp_symbol = None
        comp_symbol_error = None
        try:
            comp_variant_desc = f"{transcript}:{variant_hgvsc}"
            comp_url = (
                "https://rest.variantvalidator.org/VariantValidator/"
                f"variantvalidator/GRCh38/{comp_variant_desc}/mane_select?"
                "content-type=application%2Fjson"
            )
            comp_resp = requests.get(comp_url)
            if comp_resp.status_code == 200:
                data = comp_resp.json()
                variant_data = data.get(comp_variant_desc)
                if variant_data is None:
                    comp_symbol_error = f"'{comp_variant_desc}' key not found in comparison API response."
                else:
                    comp_symbol = variant_data.get("gene_symbol")
                    if comp_symbol is None:
                        comp_symbol_error = "Error: 'gene_symbol' not found in comparison variant data."
            else:
                comp_symbol_error = f"Comparison API call failed with status: {comp_resp.status_code}"
        except Exception as e:
            comp_symbol_error = f"Error during comparison API call: {e}"

        # -------------------------------------------------------
        # 3) Compare them using your single-record function
        # -------------------------------------------------------
        if base_symbol_error or comp_symbol_error:
            # If either is missing or had an error, store that in results
            comparison_result = base_symbol_error or comp_symbol_error
        else:
            # Both symbols are present
            comparison_result = compare_base_and_comparison(base_symbol, comp_symbol)

        # Append final results for row i
        results.append({
            "Gene": gene_query,
            "BaseGeneSymbol": base_symbol if base_symbol else None,
            "Transcript": transcript,
            "Variant (HGVSc)": variant_hgvsc,
            "ComparisonGeneSymbol": comp_symbol if comp_symbol else None,
            "ComparisonResult": comparison_result
        })

    return pd.DataFrame(results)
