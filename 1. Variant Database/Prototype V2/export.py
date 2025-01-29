def export_to_excel(df, output_path):
    """
    Exports the given DataFrame to an Excel file.

    Args:
        df (pd.DataFrame): The DataFrame to export.
        output_path (str): Path where the Excel file will be saved.

    Returns:
        None
    """
    try:
        df_filled = df.fillna('NA')
        df_filled.to_excel(output_path, index=False)
        print(f"Data successfully exported to {output_path}")
    except Exception as e:
        print(f"An error occurred while exporting to Excel: {e}")
        raise
