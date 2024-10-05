def generate_dynamic_table(data_list):
    """
    Generates a Markdown-formatted table based on a list of rows where each row can have any number of columns.
    
    Parameters:
    data_list (list): A list of lists, where each sublist represents a row in the table.
    
    Returns:
    str: A string representing the table in Markdown format.
    """
    # Check if the list is empty
    if not data_list or len(data_list) == 0:
        return "No data provided to generate a table."

    # Dynamically generate the headers based on the first row
    headers = "| " + " | ".join(data_list[0]) + " |\n"
    
    # Dynamically generate the separator row (--- for each column)
    separator = "| " + " | ".join(['---'] * len(data_list[0])) + " |\n"
    
    # Initialize rows string
    rows = ""
    
    # Loop through the remaining rows (excluding the header row)
    for row in data_list[1:]:
        # Add each row to the table (make sure it's the same length as the header row)
        row_string = "| " + " | ".join(row) + " |\n"
        rows += row_string
    
    # Combine the headers, separator, and rows
    table_markdown = headers + separator + rows
    return table_markdown