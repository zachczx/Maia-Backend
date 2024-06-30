import pandas as pd
import requests

# Function to compare categories
def compare_categories(expected, actual):
    return expected.strip().lower() == actual.strip().lower()

# Load the Excel file
file_path = 'C:\\Users\\ASUS\\Documents\\School\\Internship\\MINDEF\\clean CRM_1.xlsx'
df = pd.read_excel(file_path)

# Extract relevant columns
categories = df.iloc[1:2, 1]
case_descriptions = df.iloc[1:2, 2]

# Initialize match count
match_count = 0

# Loop through each row
for i in range(len(case_descriptions)):
    # Prepare the request payload
    payload = {'query': case_descriptions.iloc[i]}
    
    # Make the API call
    response = requests.post('http://127.0.0.1:8000/api/query/text/', json=payload)
    
    if response.status_code == 200:
        data = response.json()
        
        # Construct the category string
        category_str = data['category']
        if data['sub_category']:
            category_str += f"-{data['sub_category']}"
        if data['sub_subcategory']:
            category_str += f"-{data['sub_subcategory']}"
        
        # Compare the expected and actual categories
        if compare_categories(categories.iloc[i], category_str):
            match_count += 1
    else:
        print(f"Error with row {i+2}: {response.status_code} - {response.text}")

# Print the result
print(f"Total matches: {match_count} out of {len(case_descriptions)}")
