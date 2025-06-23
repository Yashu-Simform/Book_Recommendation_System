import re


def extract_violating_column(error_msg: str):
    """
    Extracts the column name that caused a database constraint violation from psycopg2 error messages.
    Works for multiple constraints (Unique, Foreign Key, Check, Not Null).
    """
    match = re.search(r"Key \((.*?)\)=\((.*?)\)", error_msg)
    if match:
        column_name = match.group(1)  # Extracts the column name, e.g., "email"
        conflicting_value = match.group(
            2
        )  # Extracts the conflicting value, e.g., "yashuranparia@gmail.com"
        return column_name, conflicting_value
    return None, None
