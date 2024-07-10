import pandas as pd
import requests

# Function to compare categories
def compare_categories(expected, actual):
    return expected.strip().lower() == actual.strip().lower()

file_path = 'C:\\Users\\ASUS\\Documents\\School\\Internship\\MINDEF\\clean CRM_1.xlsx'
df = pd.read_excel(file_path)

categories = df.iloc[1:2, 1]
case_descriptions = df.iloc[1:2, 2]

match_count = 0

for i in range(len(case_descriptions)):
    payload = {'query': case_descriptions.iloc[i]}
    
    response = requests.post('http://127.0.0.1:8000/api/query/text/', json=payload)
    
    if response.status_code == 200:
        data = response.json()
        
        category_str = data['category']
        # if data['sub_category']:
        #     category_str += f"-{data['sub_category']}"
        # if data['sub_subcategory']:
        #     category_str += f"-{data['sub_subcategory']}"
        
        
        if compare_categories(categories.iloc[i], category_str):
            match_count += 1
            print(f"MATCHING: {categories.iloc[i]} and {category_str} RESULT: true")
        else:
            print(f"MATCHING: {categories.iloc[i]} and {category_str} RESULT: false")
    else:
        print(f"Error with row {i+2}: {response.status_code} - {response.text}")

# Print the result
print(f"Total matches: {match_count} out of {len(case_descriptions)}")