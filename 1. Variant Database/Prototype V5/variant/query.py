import streamlit as st



def query(df):
    """
    Queries a DataFrame based on user input with case-insensitive comparison, 
    multi-word search, and optional suggestions.

    Features:
    ---------
    - Allows searching across multiple column fields.
    - Supports multi-word search.
    - Provides AND (match all words) and OR (match any word) filtering.
    - Displays autocomplete suggestions based on available data, 
      but does not override user input.
    - Offers CSV download for filtered results.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame containing data (e.g., genomic variant data).

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

    # Extract unique values from selected columns for suggestions
    unique_values = set()
    for col in selected_columns:
        unique_values.update(df[col].dropna().astype(str).unique())
    # Convert set to sorted list for better UI experience
    unique_values = sorted(unique_values)

    # =====================================================
    # 🔎 Step 2: Let user freely type search terms (no auto)
    # =====================================================
    free_text_input = st.text_input("Type your search term(s) (space or comma-separated):")

    # Optional: parse multiple terms from the user's free text
    typed_terms = []
    if free_text_input.strip():
        # Split on commas OR spaces, depending on your preference
        typed_terms = [term.strip() for term in free_text_input.replace(',', ' ').split() if term.strip()]

    # ================================================================================
    # 💡 Step 3: Let user pick from suggestions separately (NOT overriding free input)
    # ================================================================================
    user_suggestions = st.multiselect(
        "Optional: pick any suggested search terms below (these do not overwrite your text input):",
        options=unique_values,
        default=[]
    )

    # Combine typed terms + picked suggestions
    search_input = typed_terms + user_suggestions

    if not search_input:
        st.warning("Please enter at least one search term or pick from suggestions.")
        return df

    # Choose AND or OR logic
    filter_logic = st.radio("Select filter logic:", ["AND (Match All Words)", "OR (Match Any Word)"], horizontal=True)

    # ===============================
    # 🔍 Step 4: Perform the Search
    # ===============================
    with st.spinner("Searching..."):
        # For each row, we check if the row matches (all/any) of the search_input terms
        if filter_logic == "AND (Match All Words)":
            mask = df[selected_columns].apply(
                lambda row: all(
                    any(term.lower() in str(cell).lower() for cell in row) for term in search_input
                ),
                axis=1
            )
        else:  # OR logic
            mask = df[selected_columns].apply(
                lambda row: any(
                    any(term.lower() in str(cell).lower() for cell in row) for term in search_input
                ),
                axis=1
            )

        query_result = df[mask]

    # =====================================
    # 📊 Step 5: Display & Download Results
    # =====================================
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
