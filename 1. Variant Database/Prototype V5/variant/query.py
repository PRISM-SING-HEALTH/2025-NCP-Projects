import streamlit as st
import pandas as pd



def query(df: pd.DataFrame):
    """
    Queries a DataFrame based on user input with case-insensitive comparison and multi-word search.

    Features:
    ---------
    - Allows searching across multiple column fields (L2 query).
    - Supports multi-word search (separate words with spaces).
    - Provides AND (match all words) and OR (match any word) filtering.
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

    # User inputs search terms (multiple words allowed)
    search_input = st.text_input("Enter search terms (separate words with spaces)").strip()

    # If no search input, do nothing
    if not search_input:
        st.warning("Please enter at least one search term.")
        return df

    # Split user input into multiple search words
    search_terms = search_input.split()  # Splitting on spaces

    # Choose AND or OR logic
    filter_logic = st.radio("Select filter logic:", ["AND (Match All Words)", "OR (Match Any Word)"], horizontal=True)

    # ===============================
    # 🔍 Step 2: Perform Search
    # ===============================
    with st.spinner("Searching..."):
        if filter_logic == "AND (Match All Words)":
            # Each row must contain all words in at least one selected column
            mask = df[selected_columns].apply(lambda row: all(
                any(word.lower() in str(cell).lower() for cell in row) for word in search_terms
            ), axis=1)
        else:
            # Each row must contain at least one word in any selected column
            mask = df[selected_columns].apply(lambda row: any(
                any(word.lower() in str(cell).lower() for cell in row) for word in search_terms
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

