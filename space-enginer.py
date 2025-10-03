import pandas as pd
import csv
import re
import requests
import json
import faiss
import numpy as np
import time


def cleanup_data(text: str):
 
    
    # Normalize minus signs (U+2212 → hyphen)
    text = text.replace("−", "-")

    # Step 1: Decode Unicode escapes
    text = text.encode('utf-8').decode('unicode_escape')

    # Step 2: Optional: Remove extra backslashes (if any)
    text = text.replace('\\', '')
    
    # Normalize multiple spaces / weird unicode spaces
    text = re.sub(r"\s+", " ", text).strip()

    text = re.sub(r'^\s*\d+(\.\d+)*\s*\.?\s*', '', text, flags=re.MULTILINE)

    # Optional: Remove extra empty lines
    text = re.sub(r'\n\s*\n', '\n', text).strip()

    # 1. Remove figure references like (Fig. 1A), (Fig. 1B–D)
    text = re.sub(r"\(Fig\.[^)]*\)", "", text)

    # 2. Remove table references like (Table 1), (Table 2)
    text = re.sub(r"\(Table[^)]*\)", "", text)

    # Remove "Refer to Fig. X" (X can be 1, 2A, 3B–D etc.)
    text = re.sub(r"Refer to Fig\.[^\s.]*\.?", "", text)

    # 3. Remove "for full review see ..." notes
    text = re.sub(r"\(for full review see[^)]*\)", "", text, flags=re.IGNORECASE)

    return text

def fetch_space_biology_data_bioc(pmcid: str):

    
    url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/{pmcid}/unicode"
    # print(pmcid)
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching {pmcid}: {response.status_code}")
        return None

    try:
        paper_json = response.json()
        # print(paper_json)
    except Exception as e:
        print(f"Failed to parse JSON for {pmcid}: {e}")
        return None
    
    time.sleep(1)

    return paper_json



url = "https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv"
df = pd.read_csv(url)


def get_all_paper_data(df):

    paper_metadata = list()
    for index, row in df.iterrows():
        match = re.search(r'(PMC\d+)', row['Link'])
        if match:
         pmc_id = match.group(1)
         paper_metadata.append(pmc_id)

    return paper_metadata     


table_metadata_ids = get_all_paper_data(df)

def process_space_biology_data(metada_json_data):
    paragraph_data = metada_json_data[0]["documents"][0]
    passsages =paragraph_data['passages']


    rows = []
    current_l1 = None
    current_l2 = None

    for item in passsages:
        passagge_data = item["text"]
        t = item['infons']['type']
        text = cleanup_data(passagge_data)

        if t == "title_1":
            current_l1 = text
            current_l2 = None
        elif t == "title_2":
            current_l2 = text
        elif t == "paragraph":
            rows.append({
            "level_1": current_l1,
            "level_2": current_l2,
            "text": text
            })


    return rows

def fetch_all_nasa_metadata_info(metadata_list):

    metadata_raw_json_response_list=list()

    raw_json_data=fetch_space_biology_data_bioc(metadata_list[1])
    space_engine_processed_data = process_space_biology_data(raw_json_data)
    row_json = json.dumps(space_engine_processed_data)


    print(row_json)

    # for metadata_id in metadata_list:
    #     raw_json_data=fetch_space_biology_data_bioc(metadata_id)
        
    #     space_engine_processed_data = process_space_biology_data(raw_json_data)

    #     try:
    #         raw_json_data = json.loads(space_engine_processed_data)
    #         print("Valid JSON")
    #     except json.JSONDecodeError:
    #         print("Invalid JSON")

    #     metadata_raw_json_response_list.append(raw_json_data)


    # return metadata_raw_json_response_list  


metadata_raw_json_response_list=fetch_all_nasa_metadata_info(table_metadata_ids)


# print(metadata_raw_json_response_list[0])




    

# paper3_response = fetch_space_biology_data_bioc("PMC11988870")



# structured = {}
# stack = []  # keep track of nested titles
# paragraph_data = paper3_response[0]["documents"][0]
# passsages =paragraph_data['passages']


# rows = []
# current_l1 = None
# current_l2 = None

# for item in passsages:
#     passagge_data = item["text"]
#     t = item['infons']['type']
#     text = cleanup_data(passagge_data)

#     if t == "title_1":
#         current_l1 = text
#         current_l2 = None
#     elif t == "title_2":
#             current_l2 = text
#     elif t == "paragraph":
#         rows.append({
#             "level_1": current_l1,
#             "level_2": current_l2,
#             "text": text
#         })


# row_json = json.dumps(rows)        

# print(row_json)