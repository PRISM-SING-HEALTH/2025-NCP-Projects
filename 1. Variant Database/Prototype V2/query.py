def query(df):
  """
  Queries dataframe based on user input. Has case insensitive comparison.

  Args:
    df (pd.DataFrame): Input dataframe.

  Returns:
    query_result (pd.DataFrame): Query result.
  """
  print('\n### Query Dataframe ###')
  print(f"Available categories: {', '.join(df.columns)}\n")

  try:
    # User input category
    category = input('Enter category: ').strip()
    category_lower = category.lower() # convert to lower case for non-case sens.

    # Check if category exists
    categories_lower = [col.lower() for col in df.columns]
    if category_lower not in categories_lower:
      raise ValueError(f"Invalid category '{category}'. Please choose from available categories.")

    # Find actual column name (case sens match)
    category_actual = df.columns[categories_lower.index(category_lower)]

    # User input item (case insensitive and substring search)
    item = input(f"Enter item in category '{category_actual}': ").strip()

    # Handle empty item input
    if not item:
      print("Error: item cannot be empty.")
      return None

    # Query dataframe with case insensitive comparison
    query_result = df[df[category_actual].astype(str).str.contains(item, case = False, na = False)]

    if query_result.empty:
      print(f"No results found for item containing '{item}' in category '{category_actual}'.")
    else:
      print(f"Query Results for item ({len(query_result)} records(s) found):")
      return query_result

  except ValueError as e:
    print(f"Error: {e}")
    return None
