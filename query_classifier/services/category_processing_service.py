import pandas as pd
import os
import logging

logger = logging.getLogger("django")

def process_excel(file_path):
    try:
        df = pd.read_excel(file_path)

        values = df.iloc[1:, 0].tolist()

        processed_values = set()
        for value in values:
            parts = [part.strip() for part in value.split('-')]
            processed_value = '-'.join(parts)
            processed_values.add(processed_value)
        
        logger.info("Excel file read successfully")
        
        categories_file = os.path.join('query_classifier', 'config', 'categories.csv')
        if os.path.exists(categories_file):
            with open(categories_file, 'w') as f:
                f.write("CATEGORIES\n")

        categories_file = os.path.join('query_classifier', 'config', 'categories.csv')
        with open(categories_file, 'a') as f:
            for processed_value in processed_values:
                f.write(f"{processed_value}\n")
                
        logger.info("Categories written into CSV file successfully")

        return True, "Values appended successfully."

    except Exception as e:
        logger.error("Error processing Excel file or writing to CSV file")
        return False, f"Error reading or appending values: {str(e)}"
