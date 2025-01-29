import streamlit as st



def query(df):
    """
    Queries dataframe based on user input. Has case insensitive comparison.

    Args:
        df (pd.DataFrame): Input dataframe.

    Returns:
        query_result (pd.DataFrame): Query result.
    """
    st.header("Query Dataframe")

    # Display available categories
    st.write(f"Available categories: {', '.join(df.columns)}")

    # User selects a category
    category = st.selectbox("Select a category", df.columns)

    # Check if a category is selected
    if not category:
        st.warning("Please select a category to query.")
        return None

    # User inputs the item to query
    item = st.text_input(f"Enter item to search in category '{category}'")

    # Handle empty item input
    if not item:
        st.warning("Please enter an item to search.")
        return None

    # Perform the query with case-insensitive comparison
    query_result = df[df[category].astype(str).str.contains(item, case=False, na=False)]

    # Display query results
    if query_result.empty:
        st.warning(f"No results found for item containing '{item}' in category '{category}'.")
    else:
        st.success(f"Query Results ({len(query_result)} record(s) found):")
        st.write(query_result)

        # Export button to download the queried data
        csv = query_result.to_csv(index=False)
        st.download_button(
            label="Download Queried Data as CSV",
            data=csv,
            file_name="queried_data.csv",
            mime="text/csv",
        )

    return query_result
