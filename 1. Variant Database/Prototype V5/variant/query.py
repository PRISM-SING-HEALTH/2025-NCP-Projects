import streamlit as st
import pandas as pd



def query(df):
    """
    Queries a DataFrame based on user input with case-insensitive comparison, 
    multi-word search, and autocomplete suggestions.

    Features:
    ---------
    - Allows searching across multiple column fields.
    - Supports multi-word search.
    - Provides AND (match all words) and OR (match any word) filtering.
    - Implements autocomplete suggestions based on available data.
    - Offers CSV download for filtered results.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame containing genomic variant data.

    Returns:
    --------
    pandas.DataFrame
        The filtered DataFrame based on user queries.
    """
    # ========================================
    # 🏷️ Step 1: Select Categories for Search
    # ========================================
    selected_columns = st.multiselect("Select columns to search (multiple allowed)", df.columns)

    if not selected_columns:
        st.warning("Please select at least one column to search.")
        return df

    # Extract unique values from selected columns for autocomplete
    unique_values = set()
    for col in selected_columns:
        unique_values.update(df[col].dropna().astype(str).unique())

    # Convert set to sorted list for better UI experience
    unique_values = sorted(unique_values)

    # Use autocomplete search input
    search_input = st.multiselect(
        "Enter search terms (start typing for suggestions):",
        options=unique_values,
        default=[]
    )

    # If no search input, do nothing
    if not search_input:
        st.warning("Please enter at least one search term.")
        return df

    # Choose AND or OR logic
    filter_logic = st.radio("Select filter logic:", ["AND (Match All Words)", "OR (Match Any Word)"], horizontal=True)

    # ===============================
    # 🔍 Step 2: Perform Search
    # ===============================
    with st.spinner("Searching..."):
        if filter_logic == "AND (Match All Words)":
            mask = df[selected_columns].apply(lambda row: all(
                any(term.lower() in str(cell).lower() for cell in row) for term in search_input
            ), axis=1)
        else:
            mask = df[selected_columns].apply(lambda row: any(
                any(term.lower() in str(cell).lower() for cell in row) for term in search_input
            ), axis=1)

        # Apply the mask to filter the DataFrame
        query_result = df[mask]

    # ===============================
    # 📊 Step 3: Display & Download Results
    # ===============================
    if query_result.empty:
        st.warning("No results found for your search.")
    else:
        st.success(f"{len(query_result)} record(s) found.")
        st.write(query_result)

        # Export button to download the queried data
        csv = query_result.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Queried Data (CSV)",
            data=csv,
            file_name="queried_data.csv",
            mime="text/csv",
        )

    return query_result
